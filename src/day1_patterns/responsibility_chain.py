"""
🔗 责任链模式 - 增强版文档处理流水线

🎯 责任链模式核心思想：
将请求沿着处理者链传递，直到有一个处理者能够处理它。每个处理者都有机会处理请求，
如果无法处理就传递给链中的下一个处理者。

🏗️ AI工作流中的应用场景：
1. 文档预处理流水线：格式验证 → 内容提取 → AI分析 → 结果整合
2. 多级AI处理：基础分析 → 深度分析 → 结果优化 → 输出格式化
3. 错误处理链：重试机制 → 降级处理 → 错误记录 → 用户通知

💡 增强特性：
- 详细的处理链执行流程打印
- JSON格式的中间结果和最终结果
- AI服务集成状态跟踪
- 处理性能统计和分析
- 错误处理和降级机制
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re
import json
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai_service import get_ai_service


def create_safe_json_output(output_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建安全的JSON输出，避免循环引用

    Args:
        output_data: 原始输出数据

    Returns:
        Dict[str, Any]: 安全的可序列化数据
    """
    # 简化版本：只保留顶层可安全序列化的数据
    safe_output = {}

    # 只复制安全的键值对
    safe_keys = ['status', 'summary', 'processed_at']
    for key in safe_keys:
        if key in output_data:
            safe_output[key] = output_data[key]

    # 对于detailed_results，只保留基本信息
    if 'detailed_results' in output_data:
        safe_output['detailed_results'] = {
            'format_validation': {
                'valid': output_data['detailed_results'].get('format_validation', {}).get('summary', {}).get('valid', False),
                'format': output_data['detailed_results'].get('format_validation', {}).get('summary', {}).get('format', 'unknown')
            },
            'sentiment_analysis': {
                'sentiment': output_data['detailed_results'].get('sentiment_analysis', {}).get('sentiment', 'neutral'),
                'confidence': output_data['detailed_results'].get('sentiment_analysis', {}).get('confidence', 0)
            },
            'ai_summary': {
                'compression_ratio': output_data['detailed_results'].get('ai_summary', {}).get('summary_result', {}).get('compression_ratio', 0),
                'service_statistics': output_data['detailed_results'].get('ai_summary', {}).get('service_statistics', {})
            }
        }

    return safe_output


@dataclass
class ProcessingRequest:
    """🏷️ 责任链模式 - 增强版处理请求对象

    责任链模式设计要点：
    1. 数据封装：将所有处理所需数据封装在请求对象中
    2. 元数据传递：通过metadata和results字段在处理器间传递信息
    3. 处理统计：记录每个处理器的执行时间和状态
    4. JSON序列化：支持详细的调试输出和结果分析
    """
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    processing_stats: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)

    def add_result(self, key: str, value: Any) -> None:
        """添加处理结果 - 责任链中处理器间传递信息的关键机制"""
        self.results[key] = value

    def add_processing_stat(self, handler_name: str, stat_info: Dict[str, Any]) -> None:
        """添加处理器统计信息"""
        self.processing_stats[handler_name] = stat_info

    def to_json(self) -> str:
        """转换为JSON格式 - 用于详细输出和调试"""
        request_dict = {
            "content_info": {
                "length": len(self.content),
                "preview": self.content[:100] + "..." if len(self.content) > 100 else self.content,
                "word_count": len(self.content.split())
            },
            "metadata": self.metadata,
            "processing_results": self.results,
            "processing_stats": self.processing_stats,
            "elapsed_time": time.time() - self.start_time
        }
        return json.dumps(request_dict, ensure_ascii=False, indent=2)


class ProcessingResult(Enum):
    """处理结果枚举"""
    CONTINUE = "continue"  # 继续传递给下一个处理者
    STOP = "stop"          # 停止处理
    ERROR = "error"        # 处理出错


class DocumentHandler(ABC):
    """🔧 责任链模式 - 增强版文档处理器抽象基类

    责任链模式设计要点：
    1. 抽象接口：定义统一的处理接口handle()和流程控制process()
    2. 链式连接：通过next_handler形成处理链
    3. 责任传递：无法处理时自动传递给下一个处理器
    4. 统计增强：记录每个处理器的执行时间和详细信息
    """

    def __init__(self, name: str):
        self.name = name
        self.next_handler: Optional['DocumentHandler'] = None
        self.handler_id = f"{name}_{int(time.time() * 1000)}"  # 唯一标识符

    def set_next(self, handler: 'DocumentHandler') -> 'DocumentHandler':
        """设置下一个处理器 - 责任链连接的关键方法"""
        print(f"🔗 连接处理器: {self.name} ➡️ {handler.name}")
        self.next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: ProcessingRequest) -> ProcessingResult:
        """处理请求的抽象方法 - 子类必须实现"""
        pass

    def process(self, request: ProcessingRequest) -> ProcessingResult:
        """📊 增强版处理流程 - 包含详细统计和错误处理"""
        handler_start_time = time.time()

        print(f"\n🔗 【{self.name}】开始处理")
        print(f"   📋 处理器ID: {self.handler_id}")
        print(f"   ⏱️  开始时间: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

        try:
            # 记录处理器开始执行
            request.add_processing_stat(self.name, {
                "start_time": handler_start_time,
                "status": "processing",
                "handler_id": self.handler_id
            })

            # 执行具体的处理逻辑
            result = self.handle(request)

            # 计算处理时间
            processing_time = time.time() - handler_start_time

            # 更新统计信息
            request.processing_stats[self.name].update({
                "end_time": time.time(),
                "processing_time": processing_time,
                "status": "completed" if result != ProcessingResult.ERROR else "failed",
                "result": result.value
            })

            print(f"   ✅ 处理完成，耗时: {processing_time:.3f}秒")

            # 决定是否继续传递给下一个处理器
            if result == ProcessingResult.CONTINUE and self.next_handler:
                print(f"   ➡️  传递给下一个处理器: {self.next_handler.name}")
                return self.next_handler.process(request)
            elif result == ProcessingResult.STOP:
                print(f"   ⏹️  处理链在 {self.name} 处停止")
                return result
            else:
                print(f"   ❌ {self.name} 处理失败")
                return result

        except Exception as e:
            # 记录错误信息
            error_time = time.time()
            processing_time = error_time - handler_start_time

            request.processing_stats[self.name].update({
                "end_time": error_time,
                "processing_time": processing_time,
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            })

            print(f"   💥 {self.name} 处理出错: {str(e)}")
            print(f"   📝 错误类型: {type(e).__name__}")
            request.results["error"] = f"{self.name}: {str(e)}"
            return ProcessingResult.ERROR

    def print_detailed_stats(self, request: ProcessingRequest) -> None:
        """打印详细的处理器统计信息"""
        stats = request.processing_stats.get(self.name, {})
        if stats:
            print(f"\n📈 【{self.name}】详细统计:")
            print(json.dumps(stats, ensure_ascii=False, indent=6))


class FormatValidationHandler(DocumentHandler):
    """📝 格式验证处理器 - 责任链的第一个节点

    责任链模式应用：
    1. 入口验证：作为处理链的入口，确保输入数据符合要求
    2. 快速失败：提前发现问题，避免无意义的后续处理
    3. 标准化输出：为后续处理器提供统一的验证结果格式
    4. 多格式支持：支持text、markdown、html等多种格式验证
    """

    def __init__(self):
        super().__init__("格式验证")
        self.supported_formats = ['text', 'markdown', 'html']
        self.max_size = 1000000  # 1MB

        print(f"🏗️  初始化{self.name}处理器")
        print(f"   📋 支持格式: {', '.join(self.supported_formats)}")
        print(f"   📏 最大文档大小: {self.max_size:,} 字符")

    def handle(self, request: ProcessingRequest) -> ProcessingResult:
        """🔍 执行格式验证 - 责任链的第一个处理步骤"""
        content = request.content
        metadata = request.metadata

        print(f"   📊 开始验证文档...")
        print(f"   📏 文档大小: {len(content):,} 字符")
        print(f"   📝 文档格式: {metadata.get('format', 'text')}")

        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'validation_steps': [],
            'warnings': [],
            'errors': []
        }

        # 步骤1: 文档大小检查
        size_check = {
            'step': 'size_validation',
            'max_size': self.max_size,
            'actual_size': len(content),
            'passed': len(content) <= self.max_size
        }
        validation_results['validation_steps'].append(size_check)

        if not size_check['passed']:
            error_msg = f"文档过大: {len(content):,} > {self.max_size:,}"
            validation_results['errors'].append(error_msg)
            raise ValueError(error_msg)

        # 步骤2: 格式检查
        doc_format = metadata.get('format', 'text')
        format_check = {
            'step': 'format_validation',
            'requested_format': doc_format,
            'supported_formats': self.supported_formats,
            'passed': doc_format in self.supported_formats
        }
        validation_results['validation_steps'].append(format_check)

        if not format_check['passed']:
            error_msg = f"不支持的格式: {doc_format}"
            validation_results['errors'].append(error_msg)
            raise ValueError(error_msg)

        # 步骤3: 内容基本检查
        content_is_empty = not content.strip()
        content_check = {
            'step': 'content_validation',
            'is_empty': content_is_empty,
            'content_length': len(content.strip()),
            'passed': not content_is_empty
        }
        validation_results['validation_steps'].append(content_check)

        if content_is_empty:
            error_msg = "文档内容为空"
            validation_results['errors'].append(error_msg)
            raise ValueError(error_msg)

        # 步骤4: 格式特定验证
        if doc_format == 'html':
            html_validation = self._validate_html(content)
            html_check = {
                'step': 'html_specific_validation',
                'has_html_tags': html_validation,
                'passed': html_validation
            }
            validation_results['validation_steps'].append(html_check)

            if not html_validation:
                error_msg = "HTML格式无效"
                validation_results['errors'].append(error_msg)
                raise ValueError(error_msg)

        elif doc_format == 'markdown':
            markdown_validation = self._validate_markdown(content)
            markdown_check = {
                'step': 'markdown_specific_validation',
                'has_markdown_syntax': markdown_validation,
                'passed': markdown_validation
            }
            validation_results['validation_steps'].append(markdown_check)

            if not markdown_validation:
                warning_msg = "文档不包含标准Markdown语法，将作为纯文本处理"
                validation_results['warnings'].append(warning_msg)
                print(f"   ⚠️  {warning_msg}")

        # 完成验证，计算总体统计
        word_count = len(content.split())
        validation_results['summary'] = {
            'valid': len(validation_results['errors']) == 0,
            'format': doc_format,
            'size': len(content),
            'word_count': word_count,
            'line_count': content.count('\n') + 1,
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'total_warnings': len(validation_results['warnings']),
            'total_errors': len(validation_results['errors']),
            'validation_time': time.time()
        }

        # 保存验证结果到请求对象
        request.add_result('format_validation', validation_results)

        # 打印详细的验证结果
        print(f"   ✅ 格式验证通过!")
        print(f"   📊 验证统计:")
        print(f"      • 格式: {validation_results['summary']['format']}")
        print(f"      • 大小: {validation_results['summary']['size']:,} 字符")
        print(f"      • 词汇: {validation_results['summary']['word_count']:,} 词")
        print(f"      • 段落: {validation_results['summary']['paragraph_count']} 个")
        print(f"      • 警告: {validation_results['summary']['total_warnings']} 个")
        print(f"      • 错误: {validation_results['summary']['total_errors']} 个")

        if validation_results['warnings']:
            print(f"   ⚠️  警告信息:")
            for warning in validation_results['warnings']:
                print(f"      • {warning}")

        # 打印JSON格式的详细验证结果
        print(f"   📄 详细验证结果 (JSON):")
        validation_json = json.dumps(validation_results, ensure_ascii=False, indent=8)
        print(f"      {validation_json}")

        return ProcessingResult.CONTINUE

    def _validate_html(self, content: str) -> bool:
        """简单HTML格式验证"""
        # 检查基本的HTML标签
        html_pattern = r'<[^>]+>'
        return bool(re.search(html_pattern, content))

    def _validate_markdown(self, content: str) -> bool:
        """简单Markdown格式验证"""
        # 检查是否包含Markdown语法
        md_patterns = [r'^#+\s', r'\*\*.*?\*\*', r'\*.*?\*', r'\[.*?\]\(.*?\)']
        return any(re.search(pattern, content, re.MULTILINE) for pattern in md_patterns)


class ContentExtractionHandler(DocumentHandler):
    """内容提取处理器"""

    def __init__(self):
        super().__init__("内容提取")

    def handle(self, request: ProcessingRequest) -> ProcessingResult:
        content = request.content

        # 提取不同类型的内容
        extracted = {
            'text_length': len(content),
            'word_count': len(content.split()),
            'line_count': content.count('\n') + 1,
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'sentences': self._extract_sentences(content),
            'key_phrases': self._extract_key_phrases(content),
            'numbers': self._extract_numbers(content),
            'emails': self._extract_emails(content),
            'urls': self._extract_urls(content)
        }

        request.results['content_extraction'] = extracted

        print(f"   📝 提取内容: {extracted['word_count']} 词, {extracted['paragraph_count']} 段落")
        return ProcessingResult.CONTINUE

    def _extract_sentences(self, content: str) -> List[str]:
        """提取句子"""
        sentences = re.split(r'[.!?]+', content)
        return [s.strip() for s in sentences if s.strip()][:10]  # 最多返回10个句子

    def _extract_key_phrases(self, content: str) -> List[str]:
        """提取关键词短语"""
        # 简单的关键词提取（实际应用中可以使用更复杂的NLP算法）
        words = re.findall(r'\b[\u4e00-\u9fa5]+\b', content)  # 提取中文词汇
        word_freq = {}
        for word in words:
            if len(word) >= 2:  # 至少2个字
                word_freq[word] = word_freq.get(word, 0) + 1

        # 返回频率最高的5个词
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]

    def _extract_numbers(self, content: str) -> List[str]:
        """提取数字"""
        return re.findall(r'\d+\.?\d*', content)

    def _extract_emails(self, content: str) -> List[str]:
        """提取邮箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, content)

    def _extract_urls(self, content: str) -> List[str]:
        """提取URL"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, content)


class SentimentAnalysisHandler(DocumentHandler):
    """情感分析处理器"""

    def __init__(self):
        super().__init__("情感分析")
        self.positive_words = ['好', '优秀', '成功', '满意', '喜欢', '棒', '完美']
        self.negative_words = ['差', '失败', '糟糕', '不满', '讨厌', '糟糕', '错误']

    def handle(self, request: ProcessingRequest) -> ProcessingResult:
        content = request.content.lower()

        positive_count = sum(1 for word in self.positive_words if word in content)
        negative_count = sum(1 for word in self.negative_words if word in content)

        # 计算情感分数
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment = "neutral"
            confidence = 0.5
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            if sentiment_score > 0.2:
                sentiment = "positive"
            elif sentiment_score < -0.2:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            confidence = min(abs(sentiment_score) + 0.5, 1.0)

        request.results['sentiment_analysis'] = {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'analysis_details': {
                'positive_words_found': [word for word in self.positive_words if word in content],
                'negative_words_found': [word for word in self.negative_words if word in content]
            }
        }

        print(f"   😊 情感分析: {sentiment} (置信度: {confidence:.2f})")
        return ProcessingResult.CONTINUE


class AISummaryHandler(DocumentHandler):
    """🤖 AI摘要处理器 - 责任链中的AI增强节点

    责任链模式应用：
    1. AI能力集成：将LLM摘要生成能力集成到处理链中
    2. 智能分析：利用AI理解文档内容并生成高质量摘要
    3. 降级机制：AI服务不可用时自动降级到规则方法
    4. 结果标准化：为后续处理器提供结构化的AI分析结果

    技术特点：
    • DeepSeek API集成
    • 智能降级处理
    • 详细调用统计
    • JSON格式结果输出
    """

    def __init__(self, max_sentences: int = 3):
        super().__init__("AI摘要")
        self.max_sentences = max_sentences
        self.ai_call_count = 0
        self.fallback_count = 0

        print(f"🤖 初始化{self.name}处理器")
        print(f"   🎯 最大摘要句数: {self.max_sentences}")
        print(f"   🔗 AI服务状态: 已连接")

    def handle(self, request: ProcessingRequest) -> ProcessingResult:
        """🧠 执行AI摘要生成 - 责任链中的智能处理步骤"""
        content = request.content

        print(f"   🤖 开始AI摘要生成...")
        print(f"   📝 文档长度: {len(content):,} 字符")
        print(f"   🎯 目标摘要句数: {self.max_sentences}")

        ai_results = {
            'timestamp': datetime.now().isoformat(),
            'processing_status': 'started',
            'ai_service_info': {
                'provider': 'deepseek',
                'model': 'deepseek-chat',
                'max_length': 300
            },
            'performance_metrics': {
                'start_time': time.time(),
                'ai_call_time': 0,
                'total_processing_time': 0
            },
            'content_analysis': {
                'original_length': len(content),
                'word_count': len(content.split()),
                'paragraph_count': len([p for p in content.split('\n\n') if p.strip()])
            },
            'fallback_used': False,
            'errors': []
        }

        try:
            # 步骤1: 尝试使用AI服务生成摘要
            print(f"   🔗 尝试调用DeepSeek AI服务...")
            ai_call_start = time.time()

            summary = self._generate_summary(content)
            ai_call_time = time.time() - ai_call_start

            self.ai_call_count += 1
            ai_results['performance_metrics']['ai_call_time'] = ai_call_time
            ai_results['performance_metrics']['ai_success'] = True

            print(f"   ✅ AI摘要生成成功!")
            print(f"   ⏱️  AI调用耗时: {ai_call_time:.3f}秒")

        except Exception as e:
            # 步骤2: AI调用失败时使用降级方法
            error_msg = f"AI服务调用失败: {str(e)}"
            ai_results['errors'].append(error_msg)
            ai_results['fallback_used'] = True

            print(f"   ⚠️  AI服务调用失败，启用降级处理")
            print(f"   📝 错误信息: {str(e)}")

            fallback_start = time.time()
            summary = self._fallback_summary(content)
            fallback_time = time.time() - fallback_start

            self.fallback_count += 1
            ai_results['performance_metrics']['fallback_time'] = fallback_time
            ai_results['performance_metrics']['ai_success'] = False

            print(f"   ✅ 降级摘要生成完成!")
            print(f"   ⏱️  降级处理耗时: {fallback_time:.3f}秒")

        # 步骤3: 提取关键点
        print(f"   🔍 提取文档关键点...")
        key_points = self._extract_key_points(content)

        # 步骤4: 计算压缩率和其他统计信息
        compression_ratio = len(summary) / len(content) if content else 0
        total_processing_time = time.time() - ai_results['performance_metrics']['start_time']

        # 完成AI分析结果
        ai_results.update({
            'processing_status': 'completed',
            'summary_result': {
                'summary_text': summary,
                'summary_length': len(summary),
                'key_points_count': len(key_points),
                'key_points': key_points,
                'compression_ratio': compression_ratio,
                'compression_percentage': round((1 - compression_ratio) * 100, 2)
            },
            'performance_metrics': {
                **ai_results['performance_metrics'],
                'total_processing_time': total_processing_time,
                'processing_speed': len(content) / total_processing_time if total_processing_time > 0 else 0
            },
            'quality_metrics': {
                'has_summary': len(summary.strip()) > 0,
                'has_key_points': len(key_points) > 0,
                'summary_completeness': min(len(summary.split()) / 50, 1.0),  # 假设50词为完整摘要
                'key_points_relevance': len(key_points) / 5.0  # 假设5个关键点为满分
            },
            'service_statistics': {
                'total_ai_calls': self.ai_call_count,
                'total_fallbacks': self.fallback_count,
                'success_rate': (self.ai_call_count - self.fallback_count) / max(self.ai_call_count, 1) * 100
            }
        })

        # 保存AI分析结果到请求对象
        request.add_result('ai_summary', ai_results)

        # 打印详细的AI处理结果
        print(f"   🎯 AI摘要处理完成!")
        print(f"   📊 处理统计:")
        print(f"      • 摘要长度: {ai_results['summary_result']['summary_length']:,} 字符")
        print(f"      • 关键点数: {ai_results['summary_result']['key_points_count']} 个")
        print(f"      • 压缩率: {compression_ratio:.2%}")
        print(f"      • 压缩量: {ai_results['summary_result']['compression_percentage']:.1f}%")
        print(f"      • 处理速度: {ai_results['performance_metrics']['processing_speed']:.0f} 字符/秒")

        print(f"   🎨 摘要内容预览:")
        print(f"      {summary[:150]}{'...' if len(summary) > 150 else ''}")

        if key_points:
            print(f"   🔑 关键点预览:")
            for i, point in enumerate(key_points[:3], 1):
                print(f"      {i}. {point[:80]}{'...' if len(point) > 80 else ''}")
            if len(key_points) > 3:
                print(f"      ... 还有 {len(key_points) - 3} 个关键点")

        print(f"   📈 AI服务统计:")
        print(f"      • AI调用次数: {ai_results['service_statistics']['total_ai_calls']}")
        print(f"      • 降级使用次数: {ai_results['service_statistics']['total_fallbacks']}")
        print(f"      • 成功率: {ai_results['service_statistics']['success_rate']:.1f}%")

        # 打印JSON格式的详细AI处理结果
        print(f"   📄 详细AI处理结果 (JSON):")
        ai_json = json.dumps(ai_results, ensure_ascii=False, indent=8)
        print(f"      {ai_json}")

        return ProcessingResult.CONTINUE

    def _generate_summary(self, content: str) -> str:
        """🔗 使用DeepSeek AI生成智能摘要"""
        try:
            print(f"      🚀 调用DeepSeek API...")
            ai_service = get_ai_service("deepseek")

            # 构建专门的摘要请求prompt
            summary_prompt = f"""
请为以下文档生成一个简洁准确的摘要，要求：
1. 突出主要观点和核心信息
2. 保持逻辑清晰，语言流畅
3. 控制在{self.max_sentences * 30}字以内
4. 使用中文输出

文档内容：
{content}
"""

            result = ai_service.extract_summary(content, max_length=300)

            if result["success"]:
                print(f"      ✅ DeepSeek API调用成功")
                return result["content"]
            else:
                print(f"      ❌ DeepSeek API返回失败: {result.get('error', '未知错误')}")
                raise Exception(f"AI API返回错误: {result.get('error', '未知错误')}")

        except Exception as e:
            print(f"      💥 DeepSeek API调用异常: {str(e)}")
            raise Exception(f"AI服务调用失败: {str(e)}")

    def _fallback_summary(self, content: str) -> str:
        """降级摘要生成方法"""
        sentences = re.split(r'[.!?。！？]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= self.max_sentences:
            return '. '.join(sentences)

        # 简单的摘要策略：选择前面和后面的句子
        selected_sentences = sentences[:self.max_sentences//2] + sentences[-self.max_sentences//2:]

        return '. '.join(selected_sentences) + '.'

    def _extract_key_points(self, content: str) -> List[str]:
        """提取关键点"""
        # 简单的关键点提取策略
        sentences = re.split(r'[.!?。！？]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 选择包含数字或重要词汇的句子作为关键点
        important_keywords = ['重要', '关键', '核心', '主要', '必须', '应该', '需要']

        key_points = []
        for sentence in sentences:
            if (any(keyword in sentence for keyword in important_keywords) or
                re.search(r'\d+', sentence)):  # 包含数字
                key_points.append(sentence[:100] + '...' if len(sentence) > 100 else sentence)
                if len(key_points) >= 5:
                    break

        return key_points or sentences[:3]  # 如果没有找到关键点，返回前3个句子


class QualityCheckHandler(DocumentHandler):
    """质量检查处理器"""

    def __init__(self, min_quality_score: float = 0.6):
        super().__init__("质量检查")
        self.min_quality_score = min_quality_score

    def handle(self, request: ProcessingRequest) -> ProcessingResult:
        content = request.content
        metadata = request.metadata

        # 计算质量分数
        quality_score = self._calculate_quality_score(content, metadata)

        quality_issues = []
        if quality_score < self.min_quality_score:
            quality_issues = self._identify_quality_issues(content)

        request.results['quality_check'] = {
            'score': quality_score,
            'passed': quality_score >= self.min_quality_score,
            'issues': quality_issues,
            'recommendations': self._get_recommendations(quality_score, quality_issues)
        }

        if quality_score < self.min_quality_score:
            print(f"   ⚠️  质量检查未通过: {quality_score:.2f} < {self.min_quality_score}")
            # 可以选择继续处理或停止
            return ProcessingResult.CONTINUE
        else:
            print(f"   ✅ 质量检查通过: {quality_score:.2f}")
            return ProcessingResult.CONTINUE

    def _calculate_quality_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """计算文档质量分数"""
        score = 0.0

        # 长度分数 (0-0.3)
        word_count = len(content.split())
        if 50 <= word_count <= 1000:
            score += 0.3
        elif word_count > 1000:
            score += 0.2
        else:
            score += 0.1

        # 结构分数 (0-0.3)
        if content.count('\n\n') > 0:  # 有段落
            score += 0.2
        if any(header in content for header in ['#', '##', '###']):  # 有标题
            score += 0.1

        # 内容完整性 (0-0.2)
        sentences = re.split(r'[.!?。！？]+', content)
        if len(sentences) > 1:
            score += 0.2

        # 格式正确性 (0-0.2)
        if metadata.get('format') in ['text', 'markdown', 'html']:
            score += 0.2

        return min(score, 1.0)

    def _identify_quality_issues(self, content: str) -> List[str]:
        """识别质量问题"""
        issues = []

        if len(content.strip()) < 50:
            issues.append("内容过短")

        if len(content.split()) < 10:
            issues.append("词汇量不足")

        if not re.search(r'[.!?。！？]+', content):
            issues.append("缺少句子标点")

        if content.count('\n') == 0 and len(content) > 200:
            issues.append("缺少分段")

        return issues

    def _get_recommendations(self, score: float, issues: List[str]) -> List[str]:
        """获取改进建议"""
        recommendations = []

        if score < 0.5:
            recommendations.append("建议大幅重写，增加内容深度")
        elif score < 0.7:
            recommendations.append("建议增加更多细节和结构")

        if "内容过短" in issues:
            recommendations.append("增加更多内容")

        if "缺少分段" in issues:
            recommendations.append("添加适当的段落分隔")

        if "缺少句子标点" in issues:
            recommendations.append("添加正确的标点符号")

        return recommendations


class OutputFormatterHandler(DocumentHandler):
    """输出格式化处理器"""

    def __init__(self, output_format: str = 'json'):
        super().__init__("输出格式化")
        self.output_format = output_format

    def handle(self, request: ProcessingRequest) -> ProcessingResult:
        results = request.results

        # 添加处理完成时间戳
        results['processed_at'] = self._get_timestamp()
        results['processor_chain'] = self._get_processing_chain(request)

        # 格式化输出
        formatted_output = self._format_output(results)

        request.results['final_output'] = formatted_output

        print(f"   📄 输出格式化完成: {self.output_format}")
        return ProcessingResult.STOP  # 这是最后一个处理器，所以停止

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def _get_processing_chain(self, request: ProcessingRequest) -> List[str]:
        """获取处理链信息"""
        # 这里应该记录实际经过的处理器
        return ["格式验证", "内容提取", "情感分析", "AI摘要", "质量检查", "输出格式化"]

    def _format_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """格式化输出结果"""
        formatted = {
            'status': 'success' if 'error' not in results else 'error',
            'summary': {
                'processing_time': results.get('processed_at'),
                'content_length': results.get('content_extraction', {}).get('text_length', 0),
                'sentiment': results.get('sentiment_analysis', {}).get('sentiment', 'unknown'),
                'quality_score': results.get('quality_check', {}).get('score', 0)
            },
            'detailed_results': results
        }

        if 'error' in results:
            formatted['error'] = results['error']

        return formatted


# 处理链构建器
class ProcessingChainBuilder:
    """处理链构建器"""

    def __init__(self):
        self.handlers = []

    def add_handler(self, handler: DocumentHandler) -> 'ProcessingChainBuilder':
        """添加处理器"""
        self.handlers.append(handler)
        return self

    def build(self) -> DocumentHandler:
        """构建处理链"""
        if not self.handlers:
            raise ValueError("至少需要一个处理器")

        # 连接所有处理器
        for i in range(len(self.handlers) - 1):
            self.handlers[i].set_next(self.handlers[i + 1])

        return self.handlers[0]

    def create_default_chain(self) -> DocumentHandler:
        """创建默认的处理链"""
        return (
            self.add_handler(FormatValidationHandler())
            .add_handler(ContentExtractionHandler())
            .add_handler(SentimentAnalysisHandler())
            .add_handler(AISummaryHandler())
            .add_handler(QualityCheckHandler())
            .add_handler(OutputFormatterHandler())
            .build()
        )


# 增强版示例使用
if __name__ == "__main__":
    print("🔗 责任链模式 - 增强版演示")
    print("="*80)
    print("🎯 演示目标：展示增强的责任链处理流程，包括AI集成、详细统计和JSON输出")
    print("="*80)

    # 创建处理链
    print("\n🏗️  构建处理链...")
    chain_builder = ProcessingChainBuilder()
    processing_chain = chain_builder.create_default_chain()

    # 测试文档 - 更丰富的内容用于展示各种处理功能
    test_content = """
    # AI驱动的智能文档处理系统项目总结

    ## 项目概述

    本项目在2024年取得了非常显著的成果！我们的开发团队表现出色，成功完成了所有预定目标。
    这是一个结合了人工智能技术的创新项目，旨在提供智能化的文档处理解决方案。

    ## 核心成就

    我们开发了三个核心模块：
    1. **智能用户管理模块** - 基于机器学习的用户行为分析
    2. **高性能数据处理引擎** - 支持TB级数据实时处理
    3. **AI增强的报告生成系统** - 自动化生成深度分析报告

    ## 关键数据指标

    📈 **性能提升数据**：
    - 用户满意度从75%提升至95%，提升了20个百分点
    - 系统性能提升50%，响应时间从200ms降至100ms
    - 运营成本降低30%，每年节省约500万元

    🔍 **技术指标**：
    - 系统可用性达到99.9%
    - 日处理文档数量：100万+份
    - API调用量：日均5000万次
    - 数据处理准确率：98.7%

    ## 团队协作

    这个项目的成功离不开团队的紧密合作！我们的开发团队、产品团队和AI研究团队共同努力，
    克服了重重技术挑战，最终交付了这个卓越的产品。

    ## 联系方式

    - 项目负责人：张明博士
    - 邮箱：zhangming@aidocs.example.com
    - 技术支持：tech-support@aidocs.example.com
    - 官方网站：https://aidocs.example.com/smart-processor

    ## 结论

    总的来说，这个AI驱动的文档处理系统项目取得了巨大成功！它不仅提升了我们的技术实力，
    也为客户创造了显著的价值。我们相信这个系统将在未来的文档处理领域发挥重要作用。
    """

    # 创建增强版处理请求
    request = ProcessingRequest(
        content=test_content,
        metadata={
            'format': 'markdown',
            'author': '张明博士',
            'created_date': '2024-01-15',
            'project_id': 'AI_DOCS_2024_001',
            'department': 'AI研发部',
            'priority': 'high',
            'tags': ['AI', '文档处理', '项目总结', '技术创新']
        }
    )

    print("\n📄 处理文档信息:")
    print("-" * 60)
    print(f"📝 文档标题: AI驱动的智能文档处理系统项目总结")
    print(f"👤 作者: {request.metadata['author']}")
    print(f"📅 创建日期: {request.metadata['created_date']}")
    print(f"📊 内容长度: {len(test_content):,} 字符")
    print(f"🔢 词汇数量: {len(test_content.split()):,} 词")
    print(f"📑 段落数量: {len([p for p in test_content.split('\n\n') if p.strip()])} 个")
    print(f"🏷️  标签: {', '.join(request.metadata['tags'])}")
    print("-" * 60)

    print("\n📄 文档内容预览:")
    print("-" * 60)
    print(test_content[:300] + "...")
    print("-" * 60)

    # 执行增强版处理链
    print("\n🚀 开始执行责任链处理...")
    print("="*60)

    chain_start_time = time.time()
    result = processing_chain.process(request)
    total_chain_time = time.time() - chain_start_time

    print("\n" + "="*60)
    print("📊 责任链处理完成 - 综合统计报告")
    print("="*60)

    # 显示总体处理统计
    print(f"\n⏱️  处理链总耗时: {total_chain_time:.3f}秒")
    print(f"📋 经过的处理器数量: {len(request.processing_stats)}")
    print(f"✅ 处理状态: {'失败' if 'error' in request.results else '成功'}")

    # 显示各处理器的详细统计
    print(f"\n📈 各处理器详细统计:")
    print("-" * 60)
    total_processing_time = 0
    for handler_name, stats in request.processing_stats.items():
        processing_time = stats.get('processing_time', 0)
        total_processing_time += processing_time
        status = stats.get('status', 'unknown')
        print(f"🔧 {handler_name}:")
        print(f"   • 处理时间: {processing_time:.3f}秒")
        print(f"   • 状态: {status}")
        print(f"   • 处理器ID: {stats.get('handler_id', 'N/A')}")
        if 'error' in stats:
            print(f"   • 错误: {stats['error']}")

    print(f"\n📊 处理效率分析:")
    print(f"   • 总处理时间: {total_processing_time:.3f}秒")
    print(f"   • 平均每处理器耗时: {total_processing_time / max(len(request.processing_stats), 1):.3f}秒")
    print(f"   • 文档处理速度: {len(test_content) / total_chain_time:.0f} 字符/秒")

    # 显示最终处理结果
    print(f"\n📋 最终处理结果摘要:")
    print("-" * 60)

    if 'format_validation' in request.results:
        validation = request.results['format_validation']['summary']
        print(f"✅ 格式验证: {validation['format']}格式，{validation['size']:,}字符，通过")

    if 'content_extraction' in request.results:
        extraction = request.results['content_extraction']
        print(f"📝 内容提取: {extraction['word_count']}词，{extraction['paragraph_count']}段落")

    if 'sentiment_analysis' in request.results:
        sentiment = request.results['sentiment_analysis']
        print(f"😊 情感分析: {sentiment['sentiment']} (置信度: {sentiment['confidence']:.2f})")

    if 'ai_summary' in request.results:
        ai_result = request.results['ai_summary']
        summary = ai_result['summary_result']
        print(f"🤖 AI摘要: {summary['summary_length']}字符，压缩率{summary['compression_ratio']:.2%}")
        print(f"   📈 AI调用成功率: {ai_result['service_statistics']['success_rate']:.1f}%")

    if 'quality_check' in request.results:
        quality = request.results['quality_check']
        print(f"🔍 质量检查: {quality['score']:.2f}分 ({'通过' if quality['passed'] else '未通过'})")

    # 显示最终JSON输出 - 修复循环引用问题
    print(f"\n📄 完整处理结果 (JSON格式):")
    print("="*60)
    final_output = request.results.get('final_output', {})
    if final_output:
        try:
            # 创建安全的JSON输出，移除可能导致循环引用的对象
            safe_output = create_safe_json_output(final_output)
            print(json.dumps(safe_output, ensure_ascii=False, indent=4))
        except (ValueError, TypeError) as e:
            print(f"⚠️  JSON序列化失败: {str(e)}")
            print("📄 输出简化版本:")
            simplified_output = {
                "status": final_output.get('status', 'unknown'),
                "summary": final_output.get('summary', {}),
                "timestamp": datetime.now().isoformat()
            }
            print(json.dumps(simplified_output, ensure_ascii=False, indent=2))
    else:
        print("⚠️  最终输出为空，可能处理过程中出现错误")

    print("\n" + "="*60)
    print("🎉 责任链模式增强版演示完成！")
    print("💡 主要增强特性:")
    print("   • 详细的处理流程追踪和统计")
    print("   • AI服务集成与智能降级机制")
    print("   • JSON格式的结构化输出")
    print("   • 全面的错误处理和性能监控")
    print("   • 可扩展的处理器架构")
    print("="*60)