"""
策略模式 - 文档处理策略

策略模式允许在运行时选择算法的行为。在AI工作流中，我们可以定义不同的文档处理策略，
根据文档类型、长度或内容特点选择最合适的处理方法。

核心思想：
- 定义算法族（不同的文档处理策略）
- 封装每种算法（具体的处理策略实现）
- 在运行时选择合适的算法（根据文档类型）
- 客户代码通过策略接口与算法交互，无需了解具体实现

适用场景：
- AI文档分析系统中不同类型文档的处理
- 内容分类处理
- 数据预处理流程中的多种算法选择

优势：
- 开闭-封闭原则：对扩展开放，对修改封闭
- 避免多重条件语句
- 提高代码的可维护性和复用性
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import sys
import os
import time
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai_service import get_ai_service
from dataclasses import dataclass


@dataclass
class Document:
    """文档数据类"""
    content: str
    title: str = ""
    doc_type: str = "general"  # legal, technical, academic, general
    length: int = 0

    def __post_init__(self):
        self.length = len(self.content)


class DocumentProcessingStrategy(ABC):
    """
    文档处理策略抽象基类

    这是策略模式中的"策略接口"，定义了所有具体策略必须实现的方法。

    设计原则：
    - 每个具体策略都实现相同的接口
    - 接口方法应该具有清晰的语义
    - 参数和返回值类型应该保持一致
    """

    @abstractmethod
    def process(self, document: Document) -> Dict[str, Any]:
        """
        处理文档的核心方法

        Args:
            document: 待处理的文档对象

        Returns:
            Dict[str, Any]: 处理结果，包含策略类型、分块数、处理片段等

        注意：每个策略的具体实现都不同，但返回格式应该保持一致
        """
        pass

    @abstractmethod
    def get_chunk_size(self, document: Document) -> int:
        """
        获取推荐的分块大小

        Args:
            document: 待处理的文档对象

        Returns:
            int: 推荐的分块大小（字符数）

        说明：不同类型的文档可能需要不同的分块策略
        - 法律文档：小块（保持条款完整性）
        - 技术文档：中等块（可以包含代码）
        - 学术文档：大块（保持论证完整性）
        """
        pass


class LegalDocumentStrategy(DocumentProcessingStrategy):
    """
    法律文档处理策略 - 具体策略实现

    这是策略模式中的"具体策略"之一，专门处理法律类文档。

    处理特点：
    - 专注法律条款、合同内容、法规文本
    - 提取关键法律概念、当事人、时间地点
    - 识别法律责任和义务
    - 小块分割以保持条款完整性
    """

    def process(self, document: Document) -> Dict[str, Any]:
        """
        处理法律文档的主流程

        处理步骤：
        1. 获取适合法律文档的分块大小
        2. 按段落分割文档（保持条款完整性）
        3. 对每个分块调用AI分析
        4. 汇总处理结果
        """
        print(f"📋 [策略启动] 使用法律文档策略处理: {document.title}")
        print(f"📏 [分块配置] 获取法律文档推荐的分块大小...")

        chunk_size = self.get_chunk_size(document)
        print(f"📊 [分块大小] {chunk_size} 字符")

        print(f"✂️  [文档分块] 开始分割文档...")
        chunks = self._split_document(document.content, chunk_size)
        print(f"🔢 [分块结果] 共分割为 {len(chunks)} 个处理块")

        print(f"🤖 [AI分析] 开始对每个分块进行AI分析...")
        processed_chunks = []

        for i, chunk in enumerate(chunks):
            print(f"\n📄 [处理分块 {i+1}/{len(chunks)}]")
            print(f"📝 [分块预览] {chunk[:80]}..." if len(chunk) > 80 else f"📝 [分块内容] {chunk}")

            # 构建专门用于法律文档的分析提示词
            prompt = f"""
            请分析以下法律文档片段，提取关键信息：

            片段 {i+1}/{len(chunks)}:
            {chunk}

            请提取：
            1. 关键法律条款
            2. 相关法律概念
            3. 重要的时间、地点、当事人
            4. 法律责任和义务

            以JSON格式返回结果。
            """

            # 🔥 关键步骤：调用DeepSeek API进行分析
            print(f"🌐 [API调用] 调用DeepSeek API进行法律文档分析...")
            try:
                ai_service = get_ai_service("deepseek")
                analysis_result = ai_service.analyze_document(chunk, "legal")

                if analysis_result["success"]:
                    print(f"✅ [API成功] 第{i+1}个分块分析成功")
                    usage = analysis_result.get("usage", {})
                    if usage:
                        print(f"📊 [Token使用] 输入:{usage.get('prompt_tokens', 0)} 输出:{usage.get('completion_tokens', 0)} 总计:{usage.get('total_tokens', 0)}")

                    # 🔥 新增：打印AI返回的JSON结构化数据
                    self._print_ai_analysis_result(analysis_result, i + 1)

                    processed_chunks.append({
                        "chunk_id": i,
                        "content_preview": chunk[:100] + "...",
                        "analysis": analysis_result["content"],
                        "raw_response": analysis_result,  # 保存完整的AI响应
                        "usage": usage,
                        "status": "success"
                    })
                else:
                    # API调用失败时的降级处理
                    print(f"❌ [API失败] 第{i+1}个分块分析失败: {analysis_result.get('error', '未知错误')}")
                    processed_chunks.append({
                        "chunk_id": i,
                        "content_preview": chunk[:100] + "...",
                        "analysis": "法律条款分析失败，使用默认处理",
                        "error": analysis_result.get("error", "未知错误"),
                        "status": "api_failed"
                    })
            except Exception as e:
                # 出错时的处理
                print(f"💥 [异常处理] 第{i+1}个分块处理异常: {str(e)}")
                processed_chunks.append({
                    "chunk_id": i,
                    "content_preview": chunk[:100] + "...",
                    "analysis": "法律条款分析结果（降级模式）",
                    "fallback": True,
                    "error": str(e),
                    "status": "exception"
                })

        # 📊 统计处理结果并返回
        success_count = sum(1 for chunk in processed_chunks if chunk.get("status") == "success")
        print(f"\n📈 [处理统计] 成功处理 {success_count}/{len(chunks)} 个分块")

        result = {
            "strategy": "legal",
            "total_chunks": len(chunks),
            "processed_chunks": processed_chunks,
            "success_rate": success_count / len(chunks) if chunks else 0,
            "key_points": [f"法律要点 {i+1}" for i in range(min(5, len(chunks)))],
            "processing_summary": {
                "total_successful": success_count,
                "total_failed": len(chunks) - success_count,
                "fallback_used": any(chunk.get("fallback") for chunk in processed_chunks)
            }
        }

        print(f"🎯 [策略完成] 法律文档策略处理完成")
        print(f"📋 [结果摘要] 成功率: {result['processing_summary']['total_successful']}/{result['total_chunks']} ({result['success_rate']:.1%})")

        return result

    def get_chunk_size(self, document: Document) -> int:
        """
        获取法律文档推荐的分块大小

        设计理由：
        - 法律文档需要保持条款的完整性
        - 较小的分块避免破坏法律逻辑
        - 便于AI精确识别法律概念
        """
        print(f"🔍 [分块策略] 法律文档推荐分块大小: 2000字符")
        print(f"💡 [设计理由] 保持法律条款完整性，避免破坏法律逻辑")
        return 2000

    def _split_document(self, content: str, chunk_size: int) -> List[str]:
        """
        按段落分割文档，保持法律条款完整性

        分割策略：
        - 优先按段落分隔符('\n\n')分割
        - 避免在段落中间分割
        - 确保每个分块都包含完整的法律段落

        Args:
            content: 文档内容
            chunk_size: 分块大小

        Returns:
            List[str]: 分割后的文档块列表
        """
        print(f"✂️  [分割算法] 使用段落分割策略")
        print(f"📝 [分割标记] 按 '\\n\\n' (段落分隔符)进行分割")

        paragraphs = content.split('\n\n')
        print(f"📊 [段落统计] 共 {len(paragraphs)} 个段落")

        chunks = []
        current_chunk = ""
        current_length = 0

        for i, paragraph in enumerate(paragraphs):
            paragraph_len = len(paragraph) + 2  # +2 for \n\n
            print(f"📄 [段落{i+1}] 长度: {paragraph_len} 字符")

            if current_length + paragraph_len <= chunk_size:
                # 可以添加到当前分块
                current_chunk += paragraph + "\n\n"
                current_length += paragraph_len
                print(f"  ➡️  添加到当前分块 (当前总长: {current_length})")
            else:
                # 需要开始新的分块
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    print(f"  📦 [分块完成] 生成第{len(chunks)}个分块，长度: {len(current_chunk)}")
                current_chunk = paragraph + "\n\n"
                current_length = paragraph_len
                print(f"  🆕 [新分块] 开始新的分块，长度: {current_length}")

        # 添加最后一个分块
        if current_chunk:
            chunks.append(current_chunk.strip())
            print(f"  📦 [最终分块] 生成第{len(chunks)}个分块，长度: {len(current_chunk)}")

        print(f"✅ [分割完成] 共生成 {len(chunks)} 个文档块")
        return chunks

    def _print_ai_analysis_result(self, analysis_result: Dict[str, Any], chunk_num: int):
        """
        📊 打印AI分析返回的JSON结构化数据

        这个方法专门用于展示AI分析结果的详细信息，包括：
        - 原始JSON响应
        - 解析后的结构化数据
        - 关键信息提取

        Args:
            analysis_result: AI分析的完整响应结果
            chunk_num: 当前分块编号
        """
        print(f"\n📋 [AI分析结果] 第{chunk_num}个分块的详细分析结果:")
        print("=" * 50)

        try:
            # 1. 打印完整的原始响应结构
            print(f"🗂️  [完整响应] AI返回的完整结构:")
            formatted_response = json.dumps(analysis_result, indent=2, ensure_ascii=False)
            print(formatted_response)

            # 2. 提取并打印分析内容
            if "content" in analysis_result:
                print(f"\n📝 [分析内容] AI生成的法律分析:")
                print("-" * 30)
                content = analysis_result["content"]

                # 尝试解析JSON格式的内容
                if isinstance(content, str):
                    try:
                        # 尝试将内容解析为JSON
                        parsed_content = json.loads(content)
                        print(f"✅ [JSON解析成功] 内容为有效的JSON格式:")
                        print(json.dumps(parsed_content, indent=2, ensure_ascii=False))

                        # 提取关键字段
                        if isinstance(parsed_content, dict):
                            print(f"\n🔍 [关键字段提取]:")
                            for key, value in parsed_content.items():
                                print(f"  📌 {key}: {value}")
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，直接打印文本内容
                        print(f"📄 [文本内容] AI分析结果:")
                        print(content)
                else:
                    print(f"📊 [数据内容] {content}")

            # 3. 打印元数据信息
            print(f"\n📊 [元数据信息]:")

            # API信息
            if "api_info" in analysis_result:
                api_info = analysis_result["api_info"]
                print(f"  🌐 API信息:")
                print(f"    模型: {api_info.get('model', 'Unknown')}")
                print(f"    状态: {api_info.get('status', 'Unknown')}")

            # Token使用情况
            if "usage" in analysis_result:
                usage = analysis_result["usage"]
                print(f"  💰 Token统计:")
                print(f"    输入Token: {usage.get('prompt_tokens', 0)}")
                print(f"    输出Token: {usage.get('completion_tokens', 0)}")
                print(f"    总计Token: {usage.get('total_tokens', 0)}")

                # 计算成本估算（假设每1000个token约0.01元）
                total_tokens = usage.get('total_tokens', 0)
                estimated_cost = (total_tokens / 1000) * 0.01
                print(f"    💵 预估成本: ¥{estimated_cost:.4f}")

            # 处理时间信息
            if "timestamp" in analysis_result:
                timestamp = analysis_result["timestamp"]
                print(f"  ⏰ 处理时间: {timestamp}")

            # 4. 分析质量评估
            print(f"\n🎯 [质量评估]:")
            content_length = len(str(analysis_result.get("content", "")))
            print(f"  📏 内容长度: {content_length} 字符")

            if content_length > 500:
                print(f"  ✅ 内容详细度: 详细")
            elif content_length > 200:
                print(f"  ⚠️  内容详细度: 中等")
            else:
                print(f"  ❌ 内容详细度: 简略")

            # 5. JSON格式验证
            print(f"\n🔍 [格式验证]:")
            content = analysis_result.get("content", "")
            if isinstance(content, str):
                try:
                    json.loads(content)
                    print(f"  ✅ JSON格式: 有效")
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON格式: 无效 ({e})")
            else:
                print(f"  📊 数据类型: {type(content).__name__}")

        except Exception as e:
            print(f"❌ [解析错误] 无法解析AI返回结果: {str(e)}")
            print(f"📄 [原始数据] {analysis_result}")

        print("=" * 50)
        print(f"🏁 [分析完成] 第{chunk_num}个分块分析结果展示完毕\n")


class TechnicalDocumentStrategy(DocumentProcessingStrategy):
    """技术文档处理策略"""

    def process(self, document: Document) -> Dict[str, Any]:
        """处理技术文档 - 专注技术概念和代码解释"""
        print(f"💻 使用技术文档策略处理: {document.title}")

        chunk_size = self.get_chunk_size(document)
        chunks = self._split_document(document.content, chunk_size)

        processed_chunks = []
        for i, chunk in enumerate(chunks):
            prompt = f"""
            请分析以下技术文档片段：

            片段 {i+1}/{len(chunks)}:
            {chunk}

            请提取：
            1. 关键技术概念
            2. 代码片段和功能说明
            3. 技术架构和流程
            4. API接口和参数说明

            以Markdown格式返回结果。
            """

            # 调用DeepSeek API进行技术文档分析
            try:
                ai_service = get_ai_service("deepseek")
                analysis_result = ai_service.analyze_document(chunk, "technical")

                if analysis_result["success"]:
                    print(f"✅ [技术分析成功] 第{i+1}个分块分析完成")
                    # 打印AI返回的详细结果
                    self._print_technical_analysis_result(analysis_result, i + 1)

                    processed_chunks.append({
                        "chunk_id": i,
                        "content_preview": chunk[:100] + "...",
                        "analysis": analysis_result["content"],
                        "raw_response": analysis_result,
                        "usage": analysis_result.get("usage", {})
                    })
                else:
                    processed_chunks.append({
                        "chunk_id": i,
                        "content_preview": chunk[:100] + "...",
                        "analysis": "技术文档分析失败，使用默认处理",
                        "error": analysis_result.get("error", "未知错误")
                    })
            except Exception as e:
                processed_chunks.append({
                    "chunk_id": i,
                    "content_preview": chunk[:100] + "...",
                    "analysis": "技术文档分析结果（降级模式）",
                    "fallback": True,
                    "error": str(e)
                })

        return {
            "strategy": "technical",
            "total_chunks": len(chunks),
            "processed_chunks": processed_chunks,
            "key_concepts": [f"技术概念 {i+1}" for i in range(min(5, len(chunks)))]
        }

    def get_chunk_size(self, document: Document) -> int:
        """技术文档可以包含代码块，使用中等大小的分块"""
        return 3000

    def _split_document(self, content: str, chunk_size: int) -> List[str]:
        """按代码块和段落分割技术文档"""
        sections = content.split('\n# ')
        chunks = []
        current_chunk = ""

        for section in sections:
            # 重新添加#号（除了第一个section）
            if section != sections[0]:
                section = '#' + section

            if len(current_chunk) + len(section) <= chunk_size:
                current_chunk += section
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = section

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks or [content]  # 确保至少有一个chunk

    def _print_technical_analysis_result(self, analysis_result: Dict[str, Any], chunk_num: int):
        """
        🔧 打印技术文档AI分析的JSON结构化数据

        专门展示技术文档分析结果，包括代码识别、技术概念提取等

        Args:
            analysis_result: AI分析的完整响应结果
            chunk_num: 当前分块编号
        """
        print(f"\n💻 [技术分析结果] 第{chunk_num}个分块的详细技术分析:")
        print("=" * 50)

        try:
            # 1. 打印完整响应
            print(f"🗂️  [完整响应] AI返回的技术分析结构:")
            formatted_response = json.dumps(analysis_result, indent=2, ensure_ascii=False)
            print(formatted_response)

            # 2. 技术内容分析
            if "content" in analysis_result:
                print(f"\n🔧 [技术内容] AI提取的技术信息:")
                print("-" * 30)
                content = analysis_result["content"]

                if isinstance(content, str):
                    try:
                        # 尝试解析JSON格式
                        parsed_content = json.loads(content)
                        print(f"✅ [JSON解析成功] 技术分析为JSON格式:")
                        print(json.dumps(parsed_content, indent=2, ensure_ascii=False))

                        # 技术特定字段提取
                        if isinstance(parsed_content, dict):
                            print(f"\n🔍 [技术要素提取]:")
                            tech_keywords = ['concepts', 'apis', 'code', 'architecture', 'parameters']
                            for key, value in parsed_content.items():
                                if any(keyword in key.lower() for keyword in tech_keywords):
                                    print(f"  ⚙️  {key}: {value}")
                                else:
                                    print(f"  📌 {key}: {value}")
                    except json.JSONDecodeError:
                        print(f"📄 [技术文档] 分析结果:")
                        print(content)

                        # 简单的技术关键词搜索
                        tech_indicators = ['API', 'function', 'class', 'method', 'parameter', 'code', 'algorithm']
                        found_keywords = [indicator for indicator in tech_indicators if indicator.lower() in content.lower()]
                        if found_keywords:
                            print(f"🔍 [识别的技术指标] {', '.join(found_keywords)}")
                else:
                    print(f"📊 [数据内容] {content}")

            # 3. 元数据和技术统计
            print(f"\n📊 [技术元数据]:")

            if "usage" in analysis_result:
                usage = analysis_result["usage"]
                print(f"  💰 Token使用:")
                print(f"    输入: {usage.get('prompt_tokens', 0)} | 输出: {usage.get('completion_tokens', 0)} | 总计: {usage.get('total_tokens', 0)}")

            # 4. 技术分析质量评估
            content_length = len(str(analysis_result.get("content", "")))
            print(f"  📏 技术文档长度: {content_length} 字符")

            # 检测是否包含代码块
            content = str(analysis_result.get("content", ""))
            has_code_block = '```' in content or '`' in content
            print(f"  🖥️  包含代码块: {'是' if has_code_block else '否'}")

        except Exception as e:
            print(f"❌ [技术分析错误] 无法解析技术分析结果: {str(e)}")

        print("=" * 50)
        print(f"🏁 [技术分析完成] 第{chunk_num}个技术分析展示完毕\n")


class AcademicDocumentStrategy(DocumentProcessingStrategy):
    """学术文档处理策略"""

    def process(self, document: Document) -> Dict[str, Any]:
        """处理学术文档 - 专注研究方法和结论提取"""
        print(f"🎓 使用学术文档策略处理: {document.title}")

        chunk_size = self.get_chunk_size(document)
        chunks = self._split_document(document.content, chunk_size)

        processed_chunks = []
        for i, chunk in enumerate(chunks):
            prompt = f"""
            请分析以下学术文档片段：

            片段 {i+1}/{len(chunks)}:
            {chunk}

            请提取：
            1. 研究问题和假设
            2. 研究方法
            3. 主要发现和结论
            4. 相关研究和文献引用

            以学术格式返回结果。
            """

            # 调用DeepSeek API进行学术文档分析
            try:
                ai_service = get_ai_service("deepseek")
                analysis_result = ai_service.analyze_document(chunk, "academic")

                if analysis_result["success"]:
                    print(f"✅ [学术分析成功] 第{i+1}个分块分析完成")
                    # 打印AI返回的详细结果
                    self._print_academic_analysis_result(analysis_result, i + 1)

                    processed_chunks.append({
                        "chunk_id": i,
                        "content_preview": chunk[:100] + "...",
                        "analysis": analysis_result["content"],
                        "raw_response": analysis_result,
                        "usage": analysis_result.get("usage", {})
                    })
                else:
                    processed_chunks.append({
                        "chunk_id": i,
                        "content_preview": chunk[:100] + "...",
                        "analysis": "学术文档分析失败，使用默认处理",
                        "error": analysis_result.get("error", "未知错误")
                    })
            except Exception as e:
                processed_chunks.append({
                    "chunk_id": i,
                    "content_preview": chunk[:100] + "...",
                    "analysis": "学术文档分析结果（降级模式）",
                    "fallback": True,
                    "error": str(e)
                })

        return {
            "strategy": "academic",
            "total_chunks": len(chunks),
            "processed_chunks": processed_chunks,
            "research_contributions": [f"学术贡献 {i+1}" for i in range(min(3, len(chunks)))]
        }

    def get_chunk_size(self, document: Document) -> int:
        """学术文档需要保持论证完整性，使用较大分块"""
        return 4000

    def _split_document(self, content: str, chunk_size: int) -> List[str]:
        """按章节分割学术文档"""
        import re

        # 匹配章节标题 (如 1. Introduction, 2. Related Work, etc.)
        section_pattern = r'\n\d+\.\s+[^\n]+'
        sections = re.split(section_pattern, content)

        if len(sections) <= 1:
            # 如果没有明显的章节结构，按段落分割
            return self._split_by_paragraphs(content, chunk_size)

        chunks = []
        current_chunk = sections[0]

        for i, section in enumerate(sections[1:], 1):
            # 重新添加章节标题
            section_title = re.search(section_pattern, content[i*100:])  # 简化处理
            if section_title:
                section = section_title.group(0) + section

            if len(current_chunk) + len(section) <= chunk_size:
                current_chunk += section
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = section

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks or [content]

    def _split_by_paragraphs(self, content: str, chunk_size: int) -> List[str]:
        """按段落分割文档"""
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _print_academic_analysis_result(self, analysis_result: Dict[str, Any], chunk_num: int):
        """
        🎓 打印学术文档AI分析的JSON结构化数据

        专门展示学术文档分析结果，包括研究方法、结论、文献引用等

        Args:
            analysis_result: AI分析的完整响应结果
            chunk_num: 当前分块编号
        """
        print(f"\n🎓 [学术分析结果] 第{chunk_num}个分块的详细学术分析:")
        print("=" * 50)

        try:
            # 1. 打印完整响应
            print(f"🗂️  [完整响应] AI返回的学术分析结构:")
            formatted_response = json.dumps(analysis_result, indent=2, ensure_ascii=False)
            print(formatted_response)

            # 2. 学术内容分析
            if "content" in analysis_result:
                print(f"\n📚 [学术内容] AI提取的学术信息:")
                print("-" * 30)
                content = analysis_result["content"]

                if isinstance(content, str):
                    try:
                        # 尝试解析JSON格式
                        parsed_content = json.loads(content)
                        print(f"✅ [JSON解析成功] 学术分析为JSON格式:")
                        print(json.dumps(parsed_content, indent=2, ensure_ascii=False))

                        # 学术特定字段提取
                        if isinstance(parsed_content, dict):
                            print(f"\n🔍 [学术要素提取]:")
                            academic_keywords = ['research', 'method', 'conclusion', 'citation', 'study', 'hypothesis', 'finding']
                            for key, value in parsed_content.items():
                                if any(keyword in key.lower() for keyword in academic_keywords):
                                    print(f"  🎓 {key}: {value}")
                                else:
                                    print(f"  📌 {key}: {value}")
                    except json.JSONDecodeError:
                        print(f"📄 [学术文档] 分析结果:")
                        print(content)

                        # 学术指标搜索
                        academic_indicators = ['研究', '方法', '结论', '实验', '数据', '文献', '假设', '发现', 'theory', 'research', 'method']
                        found_indicators = [indicator for indicator in academic_indicators if indicator in content]
                        if found_indicators:
                            print(f"🔍 [识别的学术指标] {', '.join(found_indicators[:5])}")
                else:
                    print(f"📊 [数据内容] {content}")

            # 3. 学术元数据
            print(f"\n📊 [学术元数据]:")

            if "usage" in analysis_result:
                usage = analysis_result["usage"]
                print(f"  💰 Token使用:")
                print(f"    输入: {usage.get('prompt_tokens', 0)} | 输出: {usage.get('completion_tokens', 0)} | 总计: {usage.get('total_tokens', 0)}")

            # 4. 学术分析质量评估
            content_length = len(str(analysis_result.get("content", "")))
            print(f"  📏 学术文档长度: {content_length} 字符")

            # 检测学术性指标
            content = str(analysis_result.get("content", ""))
            academic_markers = ['引用', '研究', '实验', '数据', '分析', '结论', 'citation', 'reference', 'study', 'analysis']
            academic_score = sum(1 for marker in academic_markers if marker in content.lower())
            print(f"  🎯 学术性评分: {academic_score}/10 (基于关键词出现)")

            if academic_score >= 5:
                print(f"  ✅ 学术性: 强")
            elif academic_score >= 3:
                print(f"  ⚠️  学术性: 中等")
            else:
                print(f"  ❌ 学术性: 较弱")

        except Exception as e:
            print(f"❌ [学术分析错误] 无法解析学术分析结果: {str(e)}")

        print("=" * 50)
        print(f"🏁 [学术分析完成] 第{chunk_num}个学术分析展示完毕\n")


class DocumentProcessor:
    """
    文档处理器 - 策略模式中的"上下文"类

    这是策略模式的核心组件，负责：
    1. 管理所有可用的策略
    2. 根据文档类型选择合适的策略
    3. 协调策略的执行
    4. 提供统一的处理接口

    设计模式角色：
    - Context (上下文): 持有策略对象的引用
    - 策略的执行者和管理者
    - 客户代码与具体策略之间的桥梁
    """

    def __init__(self):
        """
        初始化文档处理器

        创建所有可用的文档处理策略实例
        这些策略可以在运行时动态选择和切换
        """
        print("🏭 [处理器初始化] 创建文档处理器实例")
        print("📋 [策略注册] 注册所有可用的处理策略...")

        # 🔧 策略注册表 - 策略模式的核心数据结构
        self.strategies = {
            "legal": LegalDocumentStrategy(),        # 法律文档策略
            "technical": TechnicalDocumentStrategy(), # 技术文档策略
            "academic": AcademicDocumentStrategy(),   # 学术文档策略
            "general": TechnicalDocumentStrategy()    # 通用策略（默认）
        }

        print(f"✅ [策略注册完成] 共注册 {len(self.strategies)} 个策略:")
        for name, strategy in self.strategies.items():
            print(f"  📝 {name}: {strategy.__class__.__name__}")

    def process_document(self, document: Document, strategy_name: str = None) -> Dict[str, Any]:
        """
        处理文档的主要方法 - 策略模式的核心执行逻辑

        处理流程：
        1. 策略选择 (自动或手动)
        2. 策略验证 (确保策略存在)
        3. 策略执行 (调用具体策略的process方法)
        4. 结果返回

        Args:
            document: 待处理的文档对象
            strategy_name: 可选的策略名称，如果为None则自动选择

        Returns:
            Dict[str, Any]: 处理结果
        """
        print(f"\n🎯 [开始处理] ====================")
        print(f"📄 [文档信息] 标题: {document.title}")
        print(f"📊 [文档统计] 长度: {document.length} 字符")

        # 🔍 策略选择逻辑
        if strategy_name is None:
            # 自动策略选择：根据文档类型
            strategy_name = document.doc_type
            print(f"🤖 [策略选择] 自动选择策略: {strategy_name} (基于文档类型)")
        else:
            # 手动策略指定
            print(f"👤 [策略指定] 手动指定策略: {strategy_name}")

        # ✅ 策略验证
        if strategy_name not in self.strategies:
            print(f"⚠️  [策略警告] 未知策略 '{strategy_name}'，使用默认策略")
            strategy_name = "general"

        # 🎯 获取策略实例
        strategy = self.strategies[strategy_name]
        print(f"🔧 [策略实例] 使用策略: {strategy.__class__.__name__}")

        try:
            # 🚀 执行策略 - 这是策略模式的关键调用点
            print(f"⚡ [策略执行] 开始执行 {strategy_name} 策略...")
            start_time = time.time()

            result = strategy.process(document)

            end_time = time.time()
            processing_time = end_time - start_time

            # 📊 处理结果统计
            print(f"⏱️  [执行时间] 处理耗时: {processing_time:.2f} 秒")
            print(f"📈 [处理统计] 总分块数: {result.get('total_chunks', 0)}")

            if 'success_rate' in result:
                print(f"🎯 [成功率] {result['success_rate']:.1%}")

            print(f"✅ [处理完成] 文档处理成功!")
            print(f"🏆 [使用策略] {result['strategy']} 策略")

            return result

        except Exception as e:
            print(f"💥 [处理异常] 策略执行过程中发生错误: {str(e)}")
            raise

    def add_strategy(self, name: str, strategy: DocumentProcessingStrategy):
        """
        动态添加新的处理策略

        这展示了策略模式的扩展性：
        - 可以在运行时添加新策略
        - 不需要修改现有代码
        - 符合开闭原则

        Args:
            name: 策略名称
            strategy: 策略实例
        """
        print(f"➕ [策略扩展] 添加新策略: {name} -> {strategy.__class__.__name__}")
        self.strategies[name] = strategy
        print(f"✅ [扩展完成] 策略池现在包含 {len(self.strategies)} 个策略")

    def list_available_strategies(self):
        """
        列出所有可用的策略

        用于调试和了解当前支持的文档类型
        """
        print(f"\n📋 [可用策略] 当前支持的文档处理策略:")
        for name, strategy in self.strategies.items():
            print(f"  🏷️  {name}: {strategy.__class__.__name__}")

    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """
        获取特定策略的信息

        Args:
            strategy_name: 策略名称

        Returns:
            Dict[str, Any]: 策略信息
        """
        if strategy_name not in self.strategies:
            return {"error": f"策略 '{strategy_name}' 不存在"}

        strategy = self.strategies[strategy_name]
        return {
            "name": strategy_name,
            "class": strategy.__class__.__name__,
            "module": strategy.__class__.__module__,
            "doc": strategy.__class__.__doc__ or "无文档"
        }


# ============================================================================
# 策略模式演示和测试
# ============================================================================

def demo_strategy_pattern():
    """
    策略模式完整演示

    这个演示函数展示了策略模式的完整工作流程：
    1. 创建处理器（上下文）
    2. 创建不同类型的文档
    3. 使用不同策略处理文档
    4. 展示策略选择的灵活性
    """
    print("🎯 [演示开始] 策略模式完整演示")
    print("=" * 60)

    # 步骤1: 创建文档处理器（策略模式的Context）
    print("\n📋 [步骤1] 创建文档处理器")
    processor = DocumentProcessor()

    # 展示所有可用策略
    processor.list_available_strategies()

    # 步骤2: 创建不同类型的测试文档
    print("\n📄 [步骤2] 创建测试文档")

    # 法律文档
    legal_doc = Document(
        content="""软件许可协议

第一条 许可授予
本公司特此授予您使用本软件的非独占性许可。

第二条 使用限制
1. 被许可方不得对软件进行反向工程
2. 被许可方不得将软件用于商业目的

第三条 知识产权
软件的所有知识产权归许可方所有""",
        title="软件许可协议",
        doc_type="legal"
    )

    # 技术文档
    tech_doc = Document(
        content="""# API接口文档

## 用户认证

使用JWT token进行身份验证，格式如下：
```
Authorization: Bearer <token>
```

## 接口列表

### GET /api/users
获取用户列表

**参数：**
- page: 页码 (默认1)
- size: 每页数量 (默认10)

**返回：** 用户列表JSON""",
        title="用户服务API文档",
        doc_type="technical"
    )

    # 学术文档
    academic_doc = Document(
        content="""1. 引言

本研究旨在探讨人工智能在自然语言处理领域的应用。

2. 相关工作

Smith et al. (2020) 提出了一种新的神经网络模型，在多个基准测试中取得了最先进的结果。

3. 方法

我们采用Transformer架构，结合注意力机制进行改进。

4. 结论

实验结果表明，我们的方法在准确性和效率方面都有显著提升""",
        title="基于深度学习的NLP研究",
        doc_type="academic"
    )

    # 通用文档（用于测试默认策略）
    general_doc = Document(
        content="这是一个普通的文档内容，用于测试默认的处理策略。",
        title="普通文档",
        doc_type="general"
    )

    # 显示文档信息
    documents = [legal_doc, tech_doc, academic_doc, general_doc]
    for i, doc in enumerate(documents, 1):
        print(f"  📄 文档{i}: {doc.title} (类型: {doc.doc_type}, 长度: {doc.length} 字符)")

    # 步骤3: 使用不同策略处理文档
    print("\n🔧 [步骤3] 执行策略处理")

    for i, doc in enumerate(documents, 1):
        print(f"\n{'='*60}")
        print(f"📋 [文档{i}] 处理开始: {doc.title}")
        print(f"{'='*60}")

        # 演示自动策略选择
        result = processor.process_document(doc)

        # 演示手动策略指定
        if i == 1:  # 对第一个文档也尝试手动指定策略
            print(f"\n🔄 [策略切换] 手动指定技术策略处理法律文档...")
            manual_result = processor.process_document(doc, "technical")
            print(f"📊 [对比结果] 原策略: {result['strategy']}, 手动策略: {manual_result['strategy']}")

    # 步骤4: 演示策略扩展
    print(f"\n{'='*60}")
    print("🔧 [步骤4] 演示策略扩展性")
    print(f"{'='*60}")

    # 创建自定义策略
    class CustomMarketingStrategy(DocumentProcessingStrategy):
        """营销文档策略 - 自定义策略演示"""

        def process(self, document: Document) -> Dict[str, Any]:
            print(f"📈 [自定义策略] 使用营销策略处理: {document.title}")
            return {
                "strategy": "marketing",
                "total_chunks": 1,
                "processed_chunks": [{
                    "chunk_id": 0,
                    "analysis": "营销文档分析：识别推广重点、目标受众、营销渠道等"
                }]
            }

        def get_chunk_size(self, document: Document) -> int:
            return 1500

    # 添加自定义策略
    processor.add_strategy("marketing", CustomMarketingStrategy())

    # 使用新策略
    marketing_doc = Document(
        content="这是一份营销策划方案，包含产品推广策略和市场分析。",
        title="营销策划案",
        doc_type="marketing"
    )

    print(f"📄 [使用新策略] 处理营销文档...")
    marketing_result = processor.process_document(marketing_doc)
    print(f"📊 [新策略结果] 营销策略处理完成")

    # 步骤5: 策略信息查看
    print(f"\n{'='*60}")
    print("📋 [步骤5] 策略信息查看")
    print(f"{'='*60}")

    for strategy_name in ["legal", "technical", "academic", "marketing"]:
        info = processor.get_strategy_info(strategy_name)
        print(f"🏷️  {strategy_name}: {info['class']}")

    # 演示总结
    print(f"\n{'='*60}")
    print("🎉 [演示完成] 策略模式演示总结")
    print(f"{'='*60}")
    print("""
💡 策略模式核心要点：

1. 🎯 策略接口 (DocumentProcessingStrategy)
   - 定义统一的处理接口
   - 所有具体策略都实现相同接口

2. 🏭 上下文类 (DocumentProcessor)
   - 管理策略集合
   - 负责策略选择和执行
   - 提供统一的客户端接口

3. 🔧 具体策略 (LegalDocumentStrategy, TechnicalDocumentStrategy, ...)
   - 实现具体的处理逻辑
   - 每种策略专注于特定类型文档
   - 可以独立开发和测试

4. 🚀 策略选择
   - 运行时动态选择策略
   - 基于文档类型自动选择
   - 支持手动指定策略

5. 🔌 扩展性
   - 添加新策略无需修改现有代码
   - 符合开闭原则
   - 支持运行时动态注册

策略模式的优势：
✅ 算法族封装
✅ 运行时策略切换
✅ 易于扩展和维护
✅ 避免条件分支
✅ 符合SOLID原则
""")


if __name__ == "__main__":
    # 运行策略模式演示
    demo_strategy_pattern()