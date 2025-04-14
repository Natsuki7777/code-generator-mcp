import asyncio
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from contextlib import asynccontextmanager
import time
import re
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

# Configuration
print("📋 スクリプト初期化開始...")
SERVER_PARAMS = StdioServerParameters(
    command="npx",  # Use npx directly if it's in your PATH
    args=["@playwright/mcp@latest"],
)
print(f"📋 MCP サーバーパラメータ設定完了: {SERVER_PARAMS.command} {' '.join(SERVER_PARAMS.args or [])}")

# Models
print("🤖 モデル初期化中...")
EXECUTION_MODEL = ChatOllama(
    model="qwen2.5:14b",
    temperature=0.1,
    base_url="http://localhost:11434",
)
print(f"🤖 実行モデル初期化完了: {EXECUTION_MODEL.model}")

PLANNING_MODEL = ChatOllama(
    model="qwen2.5:14b",
    temperature=0.2,
    base_url="http://localhost:11434",
)
print(f"🤖 計画モデル初期化完了: {PLANNING_MODEL.model}")

# Enhanced templates for browser navigation
print("📝 プロンプトテンプレート読み込み中...")
PLANNING_TEMPLATE = """
あなたはウェブ検索の専門家です。ユーザーの質問に答えるために最適な検索戦略を立ててください。

質問: {query}

以下のツールが利用可能です:
{tools}

検索戦略を次の形式で提供してください:
1. 検索する情報の明確化（何を正確に知る必要があるか）
2. 使用すべき検索キーワード（複数の候補、優先順位付き）
3. 確認すべき情報源（例：公式サイト、レビューサイト、比較サイトなど）
4. 情報収集の順序（どのページをいつ見るべきか）
5. 成功の基準（どのような情報が見つかれば十分か）

戦略:
"""

# Enhanced execution template with more explicit browser navigation instructions
EXECUTION_TEMPLATE = """
あなたはウェブブラウザを操作して情報を収集するエキスパートです。
以下の検索戦略に従って、必要な情報を収集してください。

検索戦略:
{plan}

現在のブラウザ状態:
{browser_state}

以下の手順で情報収集を進めてください:
1. まず「思考」: 次に何をするべきか、現在の状態から考えてください
2. 「行動」: 適切なブラウザ操作ツールを選択して実行してください
3. 「観察」: ブラウザに表示された情報を確認し、重要な情報を抽出してください
4. 「次の行動」: 必要な情報が得られるまで、異なるwebページを探索し続けてください

重要な情報を見つけたら、以下の形式で整理してください:
- 見出し: [トピック]
- 説明: [詳細情報]
- 情報源: [URL]

探索の流れ:
1. 最初は検索エンジン (https://www.google.com) から開始し、キーワードで検索
2. 検索結果から複数の有望なサイトを選び、それぞれ閲覧して情報を収集
3. 少なくとも3つ以上の異なるソースから情報を収集すること
4. 公式サイトや信頼性の高いソースを優先すること

最後に、収集した情報全体を要約して提供してください。
"""

# New function to capture browser state
BROWSER_STATE_TEMPLATE = """
ブラウザ状態を詳細に説明してください。
現在表示しているページのタイトル、URL、主要な要素（見出し、ナビゲーション、フォームなど）を含めてください。
この情報は次のブラウザ操作の計画に使用されます。
"""

class WebSearchAgent:
    """Enhanced web search agent with improved browser control flow"""
    
    def __init__(self):
        print("🔄 WebSearchAgent インスタンス作成中...")
        self.query = ""
        self.plan = None
        self.result = None
        self.evaluation = None
        self.visited_urls = set()
        self.execution_history = []
        self.browser_state = "ブラウザはまだ起動していません。"
        self.current_url = None
        self.current_page_title = None
        self.current_page_content = None
        print("🔄 WebSearchAgent インスタンス初期化完了")
    
    @asynccontextmanager
    async def connect_session(self):
        """Connect to the MCP server with proper resource management"""
        print("🔌 MCP サーバーへの接続を開始...")
        start_time = time.time()
        
        try:
            print("🔌 stdio_client コンテキストマネージャを開始...")
            async with stdio_client(SERVER_PARAMS) as transport:
                print(f"🔌 stdio_client 接続完了 ({time.time() - start_time:.2f}秒)")
                read_stream, write_stream = transport
                print(f"🔌 ストリーム取得完了: 読み込み/書き込みストリーム準備完了")
                
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔌 ClientSession インスタンス作成完了")
                    try:
                        print("🔌 セッション初期化中...")
                        init_start = time.time()
                        await session.initialize()
                        print(f"🔌 セッション初期化完了 ({time.time() - init_start:.2f}秒)")
                        
                        print("🔌 MCP ツール読み込み中...")
                        tools_start = time.time()
                        tools = await load_mcp_tools(session)
                        print(f"🔌 MCP ツール読み込み完了: {len(tools)}個のツールが利用可能 ({time.time() - tools_start:.2f}秒)")
                        
                        print(f"🔌 利用可能なツール一覧:")
                        for i, tool in enumerate(tools):
                            print(f"   {i+1}. {tool.name}: {tool.description[:50]}...")
                        
                        yield session, tools
                    finally:
                        print("🔌 セッションコンテキスト終了")
        except Exception as e:
            print(f"❌ MCP サーバー接続エラー: {e}")
            raise
        finally:
            print(f"🔌 MCP サーバー接続処理完了 (合計時間: {time.time() - start_time:.2f}秒)")
    
    async def create_search_plan(self, tools):
        """Use the planning model to create a search strategy"""
        print("\n🔍 検索計画の作成開始...")
        start_time = time.time()
        
        tools_description = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
        print(f"🔍 ツール説明を生成: {len(tools)}個のツール説明を含む")
        
        planning_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a web search planning expert."),
            HumanMessage(content=PLANNING_TEMPLATE.format(query=self.query, tools=tools_description))
        ])
        print(f"🔍 計画プロンプト作成完了: {len(planning_prompt.format_messages())}メッセージ")
        
        print("\n=== 検索計画の作成中... ===\n")
        print(f"🔍 計画モデル呼び出し開始...")
        invoke_start = time.time()
        response = await PLANNING_MODEL.ainvoke(planning_prompt.format_messages())
        print(f"🔍 計画モデル呼び出し完了 ({time.time() - invoke_start:.2f}秒)")
        
        self.plan = response.content
        print(f"🔍 検索計画取得: {len(self.plan)}文字")
        
        print("\n=== 検索計画の内容 ===\n")
        print(self.plan)
        print(f"\n🔍 検索計画作成完了 (合計時間: {time.time() - start_time:.2f}秒)")
        return self.plan
    
    async def get_browser_state(self, session, tools):
        """Get current browser state using the snapshot tool"""
        # Find snapshot tool
        snapshot_tool = next((tool for tool in tools if tool.name == "browser_snapshot"), None)
        if not snapshot_tool:
            return "ブラウザの状態を取得できません: snapshot ツールが見つかりません"
            
        try:
            # Take snapshot
            print("🔎 ブラウザ状態の取得を試みています...")
            snapshot_result = await snapshot_tool.invoke({"selector": "body"})
            
            # Get current URL
            url_tool = next((tool for tool in tools if tool.name == "browser_navigate"), None)
            if url_tool:
                # We can't directly get the URL, so we use the page title as an indicator
                title_result = await snapshot_tool.invoke({"selector": "title"})
                page_title = title_result.get("value", {}).get("name", "不明なページ")
                self.current_page_title = page_title
                
            # Process snapshot
            if isinstance(snapshot_result, dict) and "value" in snapshot_result:
                snapshot_data = snapshot_result["value"]
                self.current_page_content = json.dumps(snapshot_data, ensure_ascii=False)
                
                # Extract basic page info
                page_info = []
                page_info.append(f"ページタイトル: {self.current_page_title}")
                
                # Extract main content elements (headings, links, etc.)
                elements = []
                if "children" in snapshot_data:
                    self._extract_elements(snapshot_data, elements)
                
                # Prepare state summary
                state_summary = "\n".join([
                    "=== 現在のブラウザ状態 ===",
                    f"ページタイトル: {self.current_page_title}",
                    f"主要要素数: {len(elements)}件",
                    "主要要素:",
                    "\n".join([f"- {elem}" for elem in elements[:10]]),
                    "==========================="
                ])
                
                self.browser_state = state_summary
                print(f"🔎 ブラウザ状態を取得しました: {len(state_summary)}文字")
                return state_summary
            else:
                return "ブラウザの状態を正常に取得できませんでした"
        except Exception as e:
            print(f"❌ ブラウザ状態取得エラー: {e}")
            return f"ブラウザ状態取得中にエラーが発生しました: {str(e)}"
    
    def _extract_elements(self, node, elements, max_elements=10):
        """Helper to extract important elements from snapshot"""
        if len(elements) >= max_elements:
            return
            
        if isinstance(node, dict):
            # Check if this is an important element
            node_name = node.get("name", "")
            node_role = node.get("role", "")
            node_value = node.get("value", "")
            
            # Add headings, links, and important elements
            if node_role in ["heading", "link", "button", "textbox", "combobox"]:
                if isinstance(node_value, str) and node_value.strip():
                    elements.append(f"{node_role}: {node_value[:50]}")
                else:
                    elements.append(f"{node_role}: {node_name[:50]}")
            
            # Process children
            if "children" in node and isinstance(node["children"], list):
                for child in node["children"]:
                    self._extract_elements(child, elements, max_elements)
    
    async def execute_search(self, session, tools, max_attempts=5):
        """Execute the search using the ReAct agent with improved browser state tracking"""
        print("\n🌐 検索実行を開始...")
        start_time = time.time()
        
        if not self.plan:
            print("🌐 検索計画がありません。検索計画を作成します...")
            await self.create_search_plan(tools)
        
        # Get initial browser state
        initial_browser_state = await self.get_browser_state(session, tools)
            
        execution_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a web browsing assistant that carefully follows instructions."),
            HumanMessage(content=EXECUTION_TEMPLATE.format(
                plan=self.plan,
                browser_state=initial_browser_state
            ))
        ])
        print(f"🌐 実行プロンプト作成完了: {len(execution_prompt.format_messages())}メッセージ")
        
        initial_messages = execution_prompt.format_messages()
        print("🌐 ReActエージェント作成中...")
        agent_start = time.time()
        agent = create_react_agent(EXECUTION_MODEL, tools)
        print(f"🌐 ReActエージェント作成完了 ({time.time() - agent_start:.2f}秒)")
        
        # Track attempts
        attempt = 0
        satisfactory_result = False
        current_messages = [{"role": msg.type, "content": msg.content} for msg in initial_messages]
        print(f"🌐 初期メッセージ設定: {len(current_messages)}メッセージ")
        
        collected_data = []
        
        while attempt < max_attempts and not satisfactory_result:
            attempt += 1
            print(f"\n=== 検索試行 {attempt}/{max_attempts} ===\n")
            attempt_start = time.time()
            
            # Invoke the agent
            print(f"🌐 試行 {attempt}: エージェント呼び出し開始...")
            agent_invoke_start = time.time()
            agent_response = await agent.ainvoke({"messages": current_messages})
            print(f"🌐 試行 {attempt}: エージェント呼び出し完了 ({time.time() - agent_invoke_start:.2f}秒)")
            
            # Record the execution
            last_messages = agent_response.get("messages", [])
            self.execution_history.append(last_messages)
            print(f"🌐 試行 {attempt}: {len(last_messages)}個の新しいメッセージを受信")
            
            # Extract and print the agent's thought process
            print(f"🌐 試行 {attempt}: エージェントの思考プロセスを抽出...")
            thought_found = False
            for msg in last_messages:
                if hasattr(msg, 'content') and isinstance(msg.content, str) and "Thought:" in msg.content:
                    thought_parts = msg.content.split('Thought:')
                    for part in thought_parts[1:]:
                        thought_text = part.split('Action:')[0].strip() if 'Action:' in part else part.strip()
                        print(f"\n🤔 エージェントの思考プロセス: ")
                        print(f"{thought_text}")
                        thought_found = True
            
            if not thought_found:
                print("🌐 思考プロセスが見つかりませんでした。")
            
            # Update the browser state after actions
            updated_browser_state = await self.get_browser_state(session, tools)
            
            # Check if we've found good information
            print(f"🌐 試行 {attempt}: 結果の評価中...")
            last_ai_message = None
            for msg in reversed(last_messages):
                if hasattr(msg, 'content') and isinstance(msg.content, str) and not (
                    "Thought:" in msg.content or 
                    "Action:" in msg.content or 
                    "Observation:" in msg.content
                ):
                    last_ai_message = msg
                    break
            
            if last_ai_message:
                print(f"🌐 試行 {attempt}: 最後のAIメッセージ: {len(last_ai_message.content)}文字")
                
                # Extract URLs from the response
                print(f"🌐 試行 {attempt}: URL抽出中...")
                url_count = 0
                for line in last_ai_message.content.split('\n'):
                    if "http" in line:
                        try:
                            url_part = line.split("http")[1].split()[0].strip(",.)()")
                            url = "http" + url_part
                            self.visited_urls.add(url)
                            url_count += 1
                        except IndexError:
                            pass  # Skip malformed URLs
                print(f"🌐 試行 {attempt}: {url_count}個のURLを抽出")
                
                # Extract potentially useful information
                if "見出し:" in last_ai_message.content or "情報源:" in last_ai_message.content:
                    collected_data.append(last_ai_message.content)
                        
                # Simple heuristic for determining if we have a satisfactory result
                content_length = len(last_ai_message.content.split())
                has_sources = "情報源" in last_ai_message.content or "URL" in last_ai_message.content
                has_details = content_length > 150
                
                print(f"🌐 試行 {attempt}: 品質評価 - 文字数: {content_length}, 情報源あり: {has_sources}, 詳細あり: {has_details}")
                
                # Success criteria: We have detailed information with sources from multiple sites
                if len(collected_data) >= 3:
                    satisfactory_result = True
                    # Combine all collected data
                    self.result = "\n\n".join([
                        "=== 収集した情報 ===",
                        *collected_data,
                        f"\n=== 情報源 ===\n訪問したURL: {', '.join(list(self.visited_urls))}"
                    ])
                    print(f"\n✅ 試行 {attempt}: 十分な情報が見つかりました\n")
                    break
                elif has_details and has_sources:
                    # If we have detailed info from one source, continue but mark as potentially satisfactory
                    print(f"🌐 試行 {attempt}: 一部の情報が見つかりました - 追加の情報源を探します")
                else:
                    print(f"🌐 試行 {attempt}: 情報が不十分です - 次の試行へ進みます")
            else:
                print(f"🌐 試行 {attempt}: AIメッセージが見つかりません")
            
            # If not satisfactory, add guidance for the next attempt
            if not satisfactory_result:
                print(f"🌐 試行 {attempt}: 次の試行のための指示を追加...")
                next_instruction = {
                    "role": "user",
                    "content": f"現在の状態: {updated_browser_state}\n\n" +
                             f"これまでに収集した情報: {len(collected_data)}件\n" +
                             f"訪問したURL数: {len(self.visited_urls)}\n\n" +
                             f"次のステップを実行してください:\n" +
                             f"1. 異なる情報源を探索する（まだ訪問していないサイト）\n" +
                             f"2. 以下のキーワードで検索を行う: {self.query} 最新情報\n" +
                             f"3. 情報を見つけたら「見出し:」「説明:」「情報源:」の形式で抽出する\n" +
                             f"4. 少なくとも3つの異なる情報源から情報を収集する"
                }
                current_messages = agent_response["messages"] + [next_instruction]
                print(f"🌐 試行 {attempt}: 新しいメッセージ数: {len(current_messages)}")
            
            print(f"🌐 試行 {attempt} 完了 (所要時間: {time.time() - attempt_start:.2f}秒)")
        
        # If we didn't find a satisfactory result but collected some data
        if not satisfactory_result and collected_data:
            self.result = "\n\n".join([
                "=== 不十分ながら収集した情報 ===",
                *collected_data,
                f"\n=== 情報源 ===\n訪問したURL: {', '.join(list(self.visited_urls))}"
            ])
        
        print("\n=== 検索結果 ===\n")
        if self.result:
            print(f"✅ 検索結果: {len(self.result)}文字")
            print(self.result)
        else:
            print("❌ 十分な情報が見つかりませんでした")
        
        print(f"\n🌐 検索実行完了 (合計時間: {time.time() - start_time:.2f}秒, 試行回数: {attempt})")
        return self.result
        
    async def run_full_search(self, query: str, max_attempts: int = 5):
        """Run the complete search process with proper resource management"""
        print(f"\n🚀 完全検索プロセスを開始: クエリ「{query}」")
        overall_start = time.time()
        
        self.query = query
        print(f"🚀 検索クエリ設定: {self.query}")
        
        print(f"🚀 MCP セッション接続を開始...")
        connect_start = time.time()
        async with self.connect_session() as (session, tools):
            print(f"🚀 MCP セッション接続完了 ({time.time() - connect_start:.2f}秒)")
            
            print(f"🚀 検索計画作成を開始...")
            plan_start = time.time()
            await self.create_search_plan(tools)
            print(f"🚀 検索計画作成完了 ({time.time() - plan_start:.2f}秒)")
            
            print(f"🚀 検索実行を開始...")
            execute_start = time.time()
            await self.execute_search(session, tools, max_attempts)
            print(f"🚀 検索実行完了 ({time.time() - execute_start:.2f}秒)")
            
        print(f"\n🚀 完全検索プロセス完了 (合計時間: {time.time() - overall_start:.2f}秒)")
        
        return {
            "query": self.query,
            "plan": self.plan,
            "result": self.result,
            "visited_urls": list(self.visited_urls),
            "attempts": len(self.execution_history),
            "total_time": time.time() - overall_start
        }

async def main():
    """Main function to run the web search agent"""
    print("\n====== WebSearchAgent スクリプト実行開始 ======\n")
    main_start = time.time()
    
    search_agent = WebSearchAgent()
    
    try:
        # Get query from user or use default
        default_query = "最新のNVIDIAのGPUの情報"
        query_input = input(f"検索クエリを入力してください（または Enter で「{default_query}」）: ")
        query = query_input or default_query

        print(f"✅ 入力確認: 「{query}」")
        print("🔍 検索を開始します...")
        
        search_start = time.time()
        report = await search_agent.run_full_search(query)
        search_time = time.time() - search_start
        
        print("\n====== 検索サマリー ======")
        print(f"クエリ: {report['query']}")
        print(f"試行回数: {report['attempts']}")
        print(f"訪問URL数: {len(report['visited_urls'])}")
        print(f"訪問したURL: {', '.join(report['visited_urls'][:3])}{'...' if len(report['visited_urls']) > 3 else ''}")
        print(f"検索時間: {search_time:.2f}秒")
        
    except Exception as e:
        print(f"\n⚠️ エラーが発生しました: {e}")
        print("\n詳細なエラーログ:")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n====== WebSearchAgent スクリプト実行完了 (合計時間: {time.time() - main_start:.2f}秒) ======\n")

if __name__ == "__main__":
    print("🚀 メイン関数を実行します...")
    asyncio.run(main())
    print("🏁 メイン関数の実行が完了しました")