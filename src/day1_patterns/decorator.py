"""
装饰器模式 - 文档处理功能增强

装饰器模式允许在不修改原始对象的情况下，动态地添加新功能。
在AI工作流中，我们可以使用装饰器为文档处理添加日志、缓存、
性能监控、错误处理等功能。
"""

import time
import json
import hashlib
from functools import wraps
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai_service import get_ai_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingContext:
    """处理上下文"""
    document_id: str
    user_id: str = "default"
    session_id: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DocumentProcessor:
    """
    基础文档处理器 - 装饰器模式的"组件"类

    这是装饰器模式的核心，定义了被装饰的基本对象。
    所有装饰器都将基于这个基础处理器来增强功能。
    """

    def process(self, content: str, context: ProcessingContext) -> Dict[str, Any]:
        """
        基础处理方法 - 装饰器链的最终执行点

        这个方法是所有装饰器调用的最终目标。
        装饰器链会在调用这个方法之前或之后添加额外功能。

        Args:
            content: 文档内容
            context: 处理上下文

        Returns:
            Dict[str, Any]: 基础处理结果
        """
        print(f"🔧 [基础处理器] 开始执行基础处理逻辑")
        print(f"📄 [文档信息] ID: {context.document_id}, 用户: {context.user_id}")
        print(f"📏 [内容长度] {len(content)} 字符")
        print(f"⏰ [处理时间] {time.time():.2f}")

        # 模拟基础处理逻辑
        base_result = {
            "content": content,
            "processed_at": time.time(),
            "context": context,
            "processor_type": "base",
            "processing_stage": "base_completed"
        }

        print(f"✅ [基础处理完成] 返回基础处理结果")
        return base_result

    def batch_process(self, contents: List[str], context: ProcessingContext) -> List[Dict[str, Any]]:
        """批量处理方法"""
        results = []
        for content in contents:
            result = self.process(content, context)
            results.append(result)
        return results


class ProcessorDecorator:
    """
    文档处理器装饰器基类 - 装饰器模式的"装饰器"抽象类

    这是装饰器模式的抽象组件，定义了所有装饰器的通用接口。
    所有具体装饰器都必须继承这个基类并实现相应的增强功能。

    设计模式角色：
    - Decorator (装饰器抽象类): 定义装饰器接口，持有组件引用
    - 维护一个指向Component对象的引用
    - 定义一个与Component接口一致的接口
    """

    def __init__(self, processor: DocumentProcessor):
        """
        初始化装饰器

        Args:
            processor: 被装饰的处理器对象（组件）
        """
        print(f"🎭 [装饰器初始化] 创建装饰器: {self.__class__.__name__}")
        print(f"🔗 [装饰链] 装饰目标: {processor.__class__.__name__}")
        self.processor = processor
        print(f"✅ [装饰器就绪] {self.__class__.__name__} 已绑定到 {processor.__class__.__name__}")

    def process(self, content: str, context: ProcessingContext) -> Dict[str, Any]:
        """
        处理方法 - 装饰器模式的核心委托机制

        这个方法展示了装饰器模式的委托机制：
        1. 装饰器可以在调用被装饰对象之前执行前置操作
        2. 通过self.processor.process()调用被装饰对象
        3. 装饰器可以在调用被装饰对象之后执行后置操作

        Args:
            content: 文档内容
            context: 处理上下文

        Returns:
            Dict[str, Any]: 装饰后的处理结果
        """
        print(f"🔄 [装饰器委托] {self.__class__.__name__} 委托给 {self.processor.__class__.__name__}")

        # 直接委托给被装饰的对象 - 这是装饰器模式的核心
        result = self.processor.process(content, context)

        print(f"🔄 [委托返回] {self.processor.__class__.__name__} 返回给 {self.__class__.__name__}")
        return result

    def batch_process(self, contents: List[str], context: ProcessingContext) -> List[Dict[str, Any]]:
        """委托批量处理"""
        print(f"📦 [批量委托] {self.__class__.__name__} 批量委托给 {self.processor.__class__.__name__}")
        return self.processor.batch_process(contents, context)

    def _print_decorator_info(self, stage: str = "处理中"):
        """
        打印装饰器信息 - 用于调试和理解装饰器链

        Args:
            stage: 当前执行阶段
        """
        print(f"🎭 [装饰器信息] 类名: {self.__class__.__name__}")
        print(f"🎯 [执行阶段] {stage}")
        print(f"🔗 [装饰对象] {self.processor.__class__.__name__}")

        # 显示装饰器链结构
        current = self
        chain = []
        while hasattr(current, 'processor'):
            chain.append(current.__class__.__name__)
            if hasattr(current.processor, '__class__'):
                if isinstance(current.processor, ProcessorDecorator):
                    current = current.processor
                else:
                    chain.append(current.processor.__class__.__name__)
                    break
            else:
                break

        print(f"🔗 [装饰器链] {' -> '.join(chain)}")


class LoggingDecorator(ProcessorDecorator):
    """
    日志装饰器 - 装饰器模式的具体装饰器实现

    这是装饰器模式的"具体装饰器"之一，为处理器添加日志记录功能。
    展示了装饰器如何在不修改原始代码的情况下添加新功能。

    增强功能：
    - 处理前日志记录
    - 处理时间统计
    - 详细的处理步骤跟踪
    - JSON格式的日志输出
    """

    def __init__(self, processor: DocumentProcessor, log_level: int = logging.INFO):
        """
        初始化日志装饰器

        Args:
            processor: 被装饰的处理器
            log_level: 日志级别
        """
        super().__init__(processor)
        self.log_level = log_level
        self.log_history = []  # 存储日志历史

        print(f"📝 [日志装饰器] 初始化日志记录功能")
        print(f"📊 [日志级别] {logging.getLevelName(log_level)}")
        print(f"📚 [日志历史] 初始化日志历史记录")

    def process(self, content: str, context: ProcessingContext) -> Dict[str, Any]:
        """
        带日志的文档处理方法

        这个方法展示了装饰器模式的典型结构：
        1. 前置处理：记录开始日志
        2. 调用被装饰对象：执行实际处理
        3. 后置处理：记录结束日志和统计信息

        Args:
            content: 文档内容
            context: 处理上下文

        Returns:
            Dict[str, Any]: 添加了日志信息的处理结果
        """
        print(f"\n📝 [日志装饰器] ================ 开始执行 ================")
        self._print_decorator_info("日志记录阶段")

        # 🔥 前置增强功能 - 记录处理开始日志
        start_log = {
            "timestamp": time.time(),
            "event": "processing_started",
            "document_id": context.document_id,
            "user_id": context.user_id,
            "content_length": len(content),
            "metadata": context.metadata
        }

        print(f"🚀 [开始日志] 记录处理开始:")
        self._print_json_log(start_log, "📋")

        # 记录到日志历史
        self.log_history.append(start_log)

        # 记录处理开始时间
        start_time = time.time()
        print(f"⏰ [时间戳] 开始时间: {start_time:.3f}")

        # 🎯 调用被装饰对象 - 这是装饰器模式的核心
        print(f"🔄 [委托调用] 调用被装饰对象的处理方法...")
        result = super().process(content, context)
        print(f"🔄 [委托返回] 被装饰对象处理完成")

        # 记录处理结束时间
        end_time = time.time()
        processing_time = end_time - start_time

        # 🔥 后置增强功能 - 记录处理结束日志
        end_log = {
            "timestamp": end_time,
            "event": "processing_completed",
            "document_id": context.document_id,
            "processing_time": processing_time,
            "content_length": len(content),
            "processing_speed": len(content) / processing_time if processing_time > 0 else 0
        }

        print(f"\n🏁 [结束日志] 记录处理完成:")
        self._print_json_log(end_log, "✅")

        # 记录到日志历史
        self.log_history.append(end_log)

        # 🎯 增强返回结果 - 添加日志信息
        result["logging_info"] = {
            "start_time": start_time,
            "end_time": end_time,
            "processing_time": processing_time,
            "log_entries": len(self.log_history),
            "decorator_name": self.__class__.__name__
        }

        print(f"📊 [处理统计] 总耗时: {processing_time:.3f} 秒")
        print(f"⚡ [处理速度] {len(content) / processing_time:.1f} 字符/秒")
        print(f"📝 [日志装饰器] ================ 执行完成 ================\n")

        return result

    def _print_json_log(self, log_entry: Dict[str, Any], icon: str = "📋"):
        """
        打印JSON格式的日志

        Args:
            log_entry: 日志条目
            icon: 日志图标
        """
        try:
            formatted_log = json.dumps(log_entry, indent=2, ensure_ascii=False)
            print(f"{icon} [JSON日志]")
            for line in formatted_log.split('\n'):
                print(f"   {line}")
        except Exception as e:
            print(f"❌ [日志错误] 无法格式化日志: {str(e)}")
            print(f"📄 [原始日志] {log_entry}")

    def get_log_history(self) -> List[Dict[str, Any]]:
        """获取日志历史"""
        return self.log_history.copy()

    def get_log_summary(self) -> Dict[str, Any]:
        """获取日志摘要"""
        if not self.log_history:
            return {"total_logs": 0, "message": "暂无日志记录"}

        total_processing_time = sum(
            log.get("processing_time", 0)
            for log in self.log_history
            if log.get("event") == "processing_completed"
        )

        return {
            "total_logs": len(self.log_history),
            "completed_processes": len([log for log in self.log_history if log.get("event") == "processing_completed"]),
            "total_processing_time": total_processing_time,
            "avg_processing_time": total_processing_time / len([log for log in self.log_history if log.get("event") == "processing_completed"]) if [log for log in self.log_history if log.get("event") == "processing_completed"] else 0,
            "decorator_type": self.__class__.__name__
        }

    def batch_process(self, contents: List[str], context: ProcessingContext) -> List[Dict[str, Any]]:
        logger.log(self.log_level, f"开始批量处理 {len(contents)} 个文档")
        start_time = time.time()
        results = super().batch_process(contents, context)
        end_time = time.time()

        logger.log(self.log_level, f"批量处理完成，总耗时: {end_time - start_time:.2f} 秒")
        return results


class CacheDecorator(ProcessorDecorator):
    """
    缓存装饰器 - 装饰器模式的具体装饰器实现

    这是装饰器模式的"具体装饰器"之二，为处理器添加缓存功能。
    展示了装饰器如何提供性能优化功能而不影响原始处理逻辑。

    增强功能：
    - 智能缓存键生成
    - LRU缓存策略
    - 缓存命中率统计
    - JSON格式的缓存分析
    """

    def __init__(self, processor: DocumentProcessor, cache_size: int = 100):
        """
        初始化缓存装饰器

        Args:
            processor: 被装饰的处理器
            cache_size: 缓存容量
        """
        super().__init__(processor)
        self.cache_size = cache_size
        self.cache = {}  # 缓存存储
        self.cache_order = []  # LRU顺序
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

        print(f"💾 [缓存装饰器] 初始化缓存功能")
        print(f"📊 [缓存配置] 容量: {cache_size} 项")
        print(f"🔑 [缓存策略] LRU (最近最少使用)")
        print(f"📈 [统计初始化] 命中率、未命中率、驱逐统计")

    def _get_cache_key(self, content: str, context: ProcessingContext) -> str:
        """
        生成缓存键 - 智能缓存键生成算法

        使用内容的MD5哈希和上下文信息生成唯一的缓存键，
        确保相同内容和上下文能够命中缓存。

        Args:
            content: 文档内容
            context: 处理上下文

        Returns:
            str: 唯一的缓存键
        """
        print(f"🔑 [缓存键生成] 开始生成缓存键...")

        # 内容哈希
        content_hash = hashlib.md5(content.encode()).hexdigest()
        print(f"📝 [内容哈希] 长度: {len(content)} -> MD5: {content_hash[:8]}...")

        # 上下文哈希
        context_data = {
            "user_id": context.user_id,
            "metadata": context.metadata
        }
        context_str = json.dumps(context_data, sort_keys=True)
        context_hash = hashlib.md5(context_str.encode()).hexdigest()
        print(f"🏷️  [上下文哈希] 用户: {context.user_id} -> MD5: {context_hash[:8]}...")

        cache_key = f"{content_hash}_{context_hash}"
        print(f"🔑 [最终缓存键] {cache_key[:16]}...")
        return cache_key

    def process(self, content: str, context: ProcessingContext) -> Dict[str, Any]:
        """
        带缓存的文档处理方法

        装饰器模式的缓存实现：
        1. 前置处理：检查缓存
        2. 条件调用：缓存未命中时才调用被装饰对象
        3. 后置处理：将结果加入缓存

        Args:
            content: 文档内容
            context: 处理上下文

        Returns:
            Dict[str, Any]: 缓存或新计算的处理结果
        """
        print(f"\n💾 [缓存装饰器] ================ 开始执行 ================")
        self._print_decorator_info("缓存检查阶段")

        # 生成缓存键
        cache_key = self._get_cache_key(content, context)

        # 🔥 前置增强功能 - 缓存查找
        print(f"🔍 [缓存查找] 检查缓存键: {cache_key[:16]}...")

        if cache_key in self.cache:
            # 缓存命中
            self.cache_stats["hits"] += 1
            print(f"🎯 [缓存命中] 缓存键 {cache_key[:16]}... 找到缓存!")

            cached_result = self.cache[cache_key].copy()
            cached_result["cached"] = True
            cached_result["cache_timestamp"] = time.time()
            cached_result["cache_key"] = cache_key[:16] + "..."

            # 获取缓存年龄
            cache_age = time.time() - cached_result.get("original_timestamp", time.time())
            cached_result["cache_age"] = cache_age

            print(f"📅 [缓存信息] 缓存年龄: {cache_age:.2f} 秒")

            # 打印缓存命中信息
            cache_hit_info = {
                "cache_key": cache_key,
                "cache_age_seconds": cache_age,
                "document_id": context.document_id,
                "hit_count": self.cache_stats["hits"]
            }
            self._print_cache_info(cache_hit_info, "🎯")

            print(f"💾 [缓存装饰器] ================ 缓存命中完成 ================")
            return cached_result
        else:
            # 缓存未命中
            self.cache_stats["misses"] += 1
            print(f"❌ [缓存未命中] 缓存键 {cache_key[:16]}... 未找到缓存")
            print(f"📊 [缓存统计] 命中: {self.cache_stats['hits']}, 未命中: {self.cache_stats['misses']}")

            # 🎯 调用被装饰对象 - 缓存未命中时才执行
            print(f"🔄 [委托调用] 缓存未命中，调用被装饰对象...")
            result = super().process(content, context)
            print(f"🔄 [委托返回] 被装饰对象处理完成")

            # 🔥 后置增强功能 - 添加到缓存
            print(f"💾 [缓存存储] 将结果添加到缓存...")
            result["cached"] = False
            result["cache_key"] = cache_key[:16] + "..."
            result["original_timestamp"] = time.time()

            # 添加到缓存
            self._add_to_cache(cache_key, result)

            print(f"💾 [缓存装饰器] ================ 缓存存储完成 ================")
            return result

    def _add_to_cache(self, key: str, result: Dict[str, Any]):
        """
        添加结果到缓存 - LRU策略实现

        Args:
            key: 缓存键
            result: 处理结果
        """
        print(f"📦 [缓存管理] 添加新项到缓存...")

        # 检查缓存容量
        if len(self.cache) >= self.cache_size:
            # 缓存满，执行LRU驱逐
            print(f"⚠️  [缓存满] 缓存已满 ({len(self.cache)}/{self.cache_size})，执行LRU驱逐")
            oldest_key = self.cache_order.pop(0)
            del self.cache[oldest_key]
            self.cache_stats["evictions"] += 1
            print(f"🗑️  [LRU驱逐] 驱逐最旧缓存项: {oldest_key[:16]}...")

        # 添加新缓存项
        self.cache[key] = result.copy()
        self.cache_order.append(key)

        # 更新缓存顺序（LRU）
        if key in self.cache_order:
            self.cache_order.remove(key)
        self.cache_order.append(key)

        print(f"✅ [缓存添加] 成功添加缓存项: {key[:16]}...")
        print(f"📊 [缓存状态] 当前使用: {len(self.cache)}/{self.cache_size}")

    def _print_cache_info(self, cache_info: Dict[str, Any], icon: str = "💾"):
        """
        打印JSON格式的缓存信息

        Args:
            cache_info: 缓存信息
            icon: 信息图标
        """
        try:
            formatted_info = json.dumps(cache_info, indent=2, ensure_ascii=False)
            print(f"{icon} [缓存信息]")
            for line in formatted_info.split('\n'):
                print(f"   {line}")
        except Exception as e:
            print(f"❌ [缓存错误] 无法格式化缓存信息: {str(e)}")
            print(f"📄 [原始信息] {cache_info}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取详细缓存统计信息"""
        hit_rate = self.cache_stats["hits"] / (self.cache_stats["hits"] + self.cache_stats["misses"]) if (self.cache_stats["hits"] + self.cache_stats["misses"]) > 0 else 0

        return {
            "cache_size": len(self.cache),
            "max_size": self.cache_size,
            "cache_usage": len(self.cache) / self.cache_size,
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "hit_rate": hit_rate,
            "total_requests": self.cache_stats["hits"] + self.cache_stats["misses"],
            "decorator_type": self.__class__.__name__
        }

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self.cache_order.clear()
        print(f"🗑️  [缓存清空] 缓存已清空")

    

class PerformanceMonitorDecorator(ProcessorDecorator):
    """性能监控装饰器 - 监控处理性能"""

    def __init__(self, processor: DocumentProcessor):
        super().__init__(processor)
        self.performance_stats = {
            "total_requests": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "max_time": 0.0,
            "min_time": float('inf')
        }

    def process(self, content: str, context: ProcessingContext) -> Dict[str, Any]:
        start_time = time.time()
        result = super().process(content, context)
        end_time = time.time()

        processing_time = end_time - start_time

        # 更新性能统计
        self._update_stats(processing_time)

        # 添加性能信息到结果
        result["performance"] = {
            "processing_time": processing_time,
            "content_length": len(content),
            "chars_per_second": len(content) / processing_time if processing_time > 0 else 0
        }

        print(f"⏱️  性能统计: {processing_time:.3f}s, {len(content)}/s")
        return result

    def _update_stats(self, processing_time: float):
        """更新性能统计信息"""
        self.performance_stats["total_requests"] += 1
        self.performance_stats["total_time"] += processing_time
        self.performance_stats["avg_time"] = (
            self.performance_stats["total_time"] /
            self.performance_stats["total_requests"]
        )
        self.performance_stats["max_time"] = max(
            self.performance_stats["max_time"], processing_time
        )
        self.performance_stats["min_time"] = min(
            self.performance_stats["min_time"], processing_time
        )

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        stats = self.performance_stats.copy()
        stats["min_time"] = stats["min_time"] if stats["min_time"] != float('inf') else 0
        return stats


class RetryDecorator(ProcessorDecorator):
    """重试装饰器 - 处理失败时自动重试"""

    def __init__(self, processor: DocumentProcessor, max_retries: int = 3, delay: float = 1.0):
        super().__init__(processor)
        self.max_retries = max_retries
        self.delay = delay

    def process(self, content: str, context: ProcessingContext) -> Dict[str, Any]:
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    print(f"🔄 第 {attempt} 次重试处理: {context.document_id}")
                    time.sleep(self.delay * attempt)  # 指数退避

                result = super().process(content, context)
                result["retry_attempts"] = attempt

                if attempt > 0:
                    print(f"✅ 重试成功: {context.document_id}")

                return result

            except Exception as e:
                last_exception = e
                print(f"❌ 处理失败 (尝试 {attempt + 1}): {str(e)}")

        # 所有重试都失败了
        print(f"💥 所有重试都失败: {context.document_id}")
        raise Exception(f"处理失败，已重试 {self.max_retries} 次: {str(last_exception)}")


class AIEnhancementDecorator(ProcessorDecorator):
    """
    AI增强装饰器 - 装饰器模式的核心装饰器实现

    这是装饰器模式最重要的"具体装饰器"，为处理器添加AI智能分析功能。
    展示了装饰器如何集成复杂的第三方服务（AI API）而不影响原始代码结构。

    增强功能：
    - 情感分析
    - 文本摘要
    - 关键词提取
    - 智能分类
    - JSON格式的AI分析结果
    - AI API调用的详细日志
    """

    def __init__(self, processor: DocumentProcessor, ai_model: str = "deepseek"):
        """
        初始化AI增强装饰器

        Args:
            processor: 被装饰的处理器
            ai_model: 使用的AI模型
        """
        super().__init__(processor)
        self.ai_model = ai_model
        self.ai_stats = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "total_api_calls": 0
        }

        print(f"🤖 [AI装饰器] 初始化AI增强功能")
        print(f"🧠 [AI模型] 使用模型: {ai_model}")
        print(f"📊 [能力配置] 情感分析、文本摘要、关键词提取")
        print(f"📈 [统计初始化] API调用、成功率统计")

    def process(self, content: str, context: ProcessingContext) -> Dict[str, Any]:
        """
        带AI增强的文档处理方法

        这个方法展示了装饰器模式处理复杂增强功能的能力：
        1. 先调用被装饰对象进行基础处理
        2. 然后添加AI分析增强功能
        3. 最后合并所有结果返回

        Args:
            content: 文档内容
            context: 处理上下文

        Returns:
            Dict[str, Any]: 包含AI分析增强的处理结果
        """
        print(f"\n🤖 [AI装饰器] ================ 开始执行 ================")
        self._print_decorator_info("AI增强阶段")

        # 🎯 第一步：调用被装饰对象进行基础处理
        print(f"🔄 [步骤1] 调用被装饰对象进行基础处理...")
        base_start_time = time.time()
        base_result = super().process(content, context)
        base_end_time = time.time()
        base_processing_time = base_end_time - base_start_time

        print(f"✅ [基础处理完成] 耗时: {base_processing_time:.3f} 秒")

        # 🔥 第二步：AI增强功能
        print(f"\n🧠 [步骤2] 开始AI智能增强分析...")
        ai_start_time = time.time()

        # 增加分析统计
        self.ai_stats["total_analyses"] += 1

        try:
            # 调用真实的AI分析
            ai_analysis = self._perform_ai_analysis(content, context)
            ai_end_time = time.time()
            ai_processing_time = ai_end_time - ai_start_time

            # 更新成功统计
            self.ai_stats["successful_analyses"] += 1

            print(f"✅ [AI分析完成] 耗时: {ai_processing_time:.3f} 秒")

            # 🔥 第三步：增强返回结果
            base_result["ai_enhancement"] = {
                "model": self.ai_model,
                "provider": "deepseek",
                "analysis": ai_analysis,
                "processed_at": time.time(),
                "ai_processing_time": ai_processing_time,
                "total_processing_time": base_processing_time + ai_processing_time,
                "enhancement_successful": True
            }

            print(f"📊 [性能对比] 基础处理: {base_processing_time:.3f}s, AI分析: {ai_processing_time:.3f}s")
            print(f"📈 [总体性能] 总耗时: {base_processing_time + ai_processing_time:.3f}s")

        except Exception as e:
            # AI分析失败时的降级处理
            ai_end_time = time.time()
            ai_processing_time = ai_end_time - ai_start_time

            # 更新失败统计
            self.ai_stats["failed_analyses"] += 1

            print(f"❌ [AI分析失败] {str(e)}")
            print(f"🔄 [降级处理] 使用基础分析结果")

            # 降级分析
            fallback_analysis = self._create_fallback_analysis(content)

            base_result["ai_enhancement"] = {
                "model": self.ai_model,
                "provider": "fallback",
                "analysis": fallback_analysis,
                "processed_at": time.time(),
                "ai_processing_time": ai_processing_time,
                "error": str(e),
                "enhancement_successful": False,
                "fallback_mode": True
            }

        print(f"🤖 [AI装饰器] ================ 执行完成 ================")
        return base_result

    def _perform_ai_analysis(self, content: str, context: ProcessingContext) -> Dict[str, Any]:
        """
        执行完整的AI分析 - 调用多个AI API

        Args:
            content: 文档内容
            context: 处理上下文

        Returns:
            Dict[str, Any]: 完整的AI分析结果
        """
        print(f"🧠 [AI分析] 开始调用DeepSeek API进行多维度分析...")

        try:
            # 获取AI服务实例
            ai_service = get_ai_service("deepseek")
            print(f"🔗 [API连接] 成功连接到DeepSeek服务")

            # 🎯 并行执行多种AI分析
            print(f"\n📊 [并行分析] 开始执行3种AI分析...")

            # 1. 情感分析
            print(f"💭 [分析1] 情感分析...")
            sentiment_start = time.time()
            sentiment_result = ai_service.sentiment_analysis(content)
            sentiment_time = time.time() - sentiment_start
            self.ai_stats["total_api_calls"] += 1
            print(f"✅ [情感分析完成] 耗时: {sentiment_time:.3f}s")

            # 2. 文本摘要
            print(f"📝 [分析2] 文本摘要...")
            summary_start = time.time()
            summary_result = ai_service.extract_summary(content, 200)
            summary_time = time.time() - summary_start
            self.ai_stats["total_api_calls"] += 1
            print(f"✅ [文本摘要完成] 耗时: {summary_time:.3f}s")

            # 3. 关键词提取
            print(f"🔍 [分析3] 关键词提取...")
            keywords_start = time.time()
            keywords_result = ai_service.extract_keywords(content, 10)
            keywords_time = time.time() - keywords_start
            self.ai_stats["total_api_calls"] += 1
            print(f"✅ [关键词提取完成] 耗时: {keywords_time:.3f}s")

            # 🔥 解析和组合AI分析结果
            print(f"\n🔧 [结果处理] 解析和组合AI分析结果...")
            analysis = self._parse_ai_results(
                sentiment_result, summary_result, keywords_result, content
            )

            # 添加API调用统计
            analysis["api_call_stats"] = {
                "total_calls": 3,
                "sentiment_time": sentiment_time,
                "summary_time": summary_time,
                "keywords_time": keywords_time,
                "total_ai_time": sentiment_time + summary_time + keywords_time
            }

            print(f"📊 [API统计] 总调用次数: {self.ai_stats['total_api_calls']}")
            print(f"🎯 [AI分析] 多维度分析完成!")

            return analysis

        except Exception as e:
            print(f"💥 [AI分析错误] AI服务调用失败: {str(e)}")
            raise Exception(f"AI分析失败: {str(e)}")

    def _parse_ai_results(self, sentiment_result: Dict, summary_result: Dict,
                         keywords_result: Dict, content: str) -> Dict[str, Any]:
        """
        解析AI分析结果并提取JSON数据

        Args:
            sentiment_result: 情感分析结果
            summary_result: 摘要结果
            keywords_result: 关键词结果
            content: 原始内容

        Returns:
            Dict[str, Any]: 解析后的完整分析结果
        """
        print(f"🔍 [结果解析] 开始解析AI返回的JSON数据...")

        # 基础统计信息
        word_count = len(content.split())
        sentences = content.count('.') + content.count('!') + content.count('?')

        analysis = {
            "basic_stats": {
                "word_count": word_count,
                "sentence_count": sentences,
                "character_count": len(content),
                "avg_sentence_length": word_count / sentences if sentences > 0 else 0
            }
        }

        # 🎯 解析情感分析结果
        print(f"💭 [情感分析] 解析情感分析JSON...")
        if sentiment_result.get("success"):
            try:
                if isinstance(sentiment_result["content"], str):
                    sentiment_data = json.loads(sentiment_result["content"])
                    print(f"✅ [情感JSON] 成功解析情感分析JSON")

                    analysis["sentiment"] = {
                        "emotion": sentiment_data.get("sentiment", "neutral"),
                        "confidence": sentiment_data.get("confidence", 0.5),
                        "key_emotions": sentiment_data.get("key_emotions", []),
                        "emotional_intensity": sentiment_data.get("emotional_intensity", "medium")
                    }

                    # 打印情感分析JSON
                    self._print_ai_json_result(sentiment_data, "💭", "情感分析")
                else:
                    analysis["sentiment"] = sentiment_result["content"]
            except json.JSONDecodeError as e:
                print(f"⚠️  [情感JSON] JSON解析失败，使用降级处理: {str(e)}")
                analysis["sentiment"] = {
                    "emotion": "neutral",
                    "confidence": 0.5,
                    "parse_error": str(e)
                }
        else:
            print(f"❌ [情感API] 情感分析API调用失败")
            analysis["sentiment"] = {
                "emotion": "neutral",
                "confidence": 0.0,
                "error": sentiment_result.get("error", "未知错误")
            }

        # 🎯 解析摘要结果
        print(f"📝 [文本摘要] 处理摘要结果...")
        if summary_result.get("success"):
            analysis["summary"] = {
                "text": summary_result["content"],
                "type": "extractive",
                "length": len(summary_result["content"])
            }
            print(f"✅ [摘要完成] 摘要长度: {len(summary_result['content'])} 字符")
        else:
            analysis["summary"] = {
                "text": content[:200] + "..." if len(content) > 200 else content,
                "type": "fallback",
                "error": summary_result.get("error", "未知错误")
            }

        # 🎯 解析关键词结果
        print(f"🔍 [关键词提取] 解析关键词JSON...")
        if keywords_result.get("success"):
            try:
                if isinstance(keywords_result["content"], str):
                    keywords_data = json.loads(keywords_result["content"])
                    print(f"✅ [关键词JSON] 成功解析关键词JSON")

                    analysis["keywords"] = {
                        "list": keywords_data.get("keywords", [])[:10],
                        "categories": keywords_data.get("categories", []),
                        "key_phrases": keywords_data.get("key_phrases", [])
                    }

                    # 打印关键词分析JSON
                    self._print_ai_json_result(keywords_data, "🔍", "关键词分析")
                else:
                    analysis["keywords"] = keywords_result["content"]
            except json.JSONDecodeError as e:
                print(f"⚠️  [关键词JSON] JSON解析失败，使用降级处理: {str(e)}")
                # 降级处理：简单提取词语
                words = content.split()
                analysis["keywords"] = {
                    "list": list(set([word for word in words if len(word) > 3]))[:10],
                    "categories": [],
                    "parse_error": str(e)
                }
        else:
            print(f"❌ [关键词API] 关键词提取API调用失败")
            analysis["keywords"] = {
                "list": ["文档", "内容", "分析"],
                "categories": [],
                "error": keywords_result.get("error", "未知错误")
            }

        # 文档复杂度分析
        analysis["complexity"] = (
            "high" if word_count > 800 else
            "medium" if word_count > 300 else
            "low"
        )

        print(f"📊 [复杂度评估] 文档复杂度: {analysis['complexity']}")
        return analysis

    def _print_ai_json_result(self, json_data: Dict[str, Any], icon: str, analysis_type: str):
        """
        打印AI返回的JSON分析结果

        Args:
            json_data: AI返回的JSON数据
            icon: 图标
            analysis_type: 分析类型
        """
        print(f"\n{icon} [AI JSON结果] {analysis_type}:")
        print("=" * 40)
        try:
            formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
            for line in formatted_json.split('\n'):
                print(f"   {line}")
        except Exception as e:
            print(f"❌ [JSON格式化错误] {str(e)}")
            print(f"📄 [原始数据] {json_data}")
        print("=" * 40)

    def _create_fallback_analysis(self, content: str) -> Dict[str, Any]:
        """
        创建降级分析结果 - AI服务不可用时的备选方案

        Args:
            content: 文档内容

        Returns:
            Dict[str, Any]: 降级分析结果
        """
        print(f"🔄 [降级分析] 创建基础分析结果...")

        word_count = len(content.split())
        sentences = content.count('.') + content.count('!') + content.count('?')

        return {
            "basic_stats": {
                "word_count": word_count,
                "sentence_count": sentences,
                "character_count": len(content),
                "avg_sentence_length": word_count / sentences if sentences > 0 else 0
            },
            "sentiment": {
                "emotion": "neutral",
                "confidence": 0.5,
                "fallback_mode": True
            },
            "summary": {
                "text": content[:200] + "..." if len(content) > 200 else content,
                "type": "fallback",
                "fallback_mode": True
            },
            "keywords": {
                "list": ["文档", "处理", "分析"],
                "categories": ["通用"],
                "fallback_mode": True
            },
            "complexity": "high" if word_count > 500 else "medium" if word_count > 200 else "low",
            "fallback_mode": True,
            "error_reason": "AI服务不可用"
        }

    def get_ai_stats(self) -> Dict[str, Any]:
        """获取AI分析统计信息"""
        success_rate = (
            self.ai_stats["successful_analyses"] / self.ai_stats["total_analyses"]
            if self.ai_stats["total_analyses"] > 0 else 0
        )

        return {
            "total_analyses": self.ai_stats["total_analyses"],
            "successful_analyses": self.ai_stats["successful_analyses"],
            "failed_analyses": self.ai_stats["failed_analyses"],
            "success_rate": success_rate,
            "total_api_calls": self.ai_stats["total_api_calls"],
            "ai_model": self.ai_model,
            "decorator_type": self.__class__.__name__
        }

    def _simulate_ai_analysis(self, content: str) -> Dict[str, Any]:
        """使用DeepSeek API进行真实的AI文档分析"""
        try:
            ai_service = get_ai_service("deepseek")

            # 并行进行多种分析
            sentiment_result = ai_service.sentiment_analysis(content)
            summary_result = ai_service.extract_summary(content, 200)
            keywords_result = ai_service.extract_keywords(content, 10)

            # 基础统计信息
            word_count = len(content.split())
            sentences = content.count('.') + content.count('!') + content.count('?')

            # 组合分析结果
            analysis = {
                "stats": {
                    "word_count": word_count,
                    "sentence_count": sentences,
                    "avg_sentence_length": word_count / sentences if sentences > 0 else 0
                }
            }

            # 情感分析结果
            if sentiment_result["success"]:
                try:
                    import json
                    sentiment_data = json.loads(sentiment_result["content"])
                    analysis["sentiment"] = sentiment_data.get("sentiment", "neutral")
                    analysis["sentiment_confidence"] = sentiment_data.get("confidence", 0.5)
                    analysis["key_emotions"] = sentiment_data.get("key_emotions", [])
                except:
                    # 如果JSON解析失败，使用简单处理
                    analysis["sentiment"] = "neutral"
                    analysis["sentiment_confidence"] = 0.5
            else:
                analysis["sentiment"] = "neutral"
                analysis["sentiment_confidence"] = 0.5
                analysis["sentiment_error"] = sentiment_result.get("error", "未知错误")

            # 摘要结果
            if summary_result["success"]:
                analysis["summary"] = summary_result["content"]
            else:
                analysis["summary"] = content[:100] + "..." if len(content) > 100 else content
                analysis["summary_error"] = summary_result.get("error", "未知错误")

            # 关键词结果
            if keywords_result["success"]:
                try:
                    import json
                    keywords_data = json.loads(keywords_result["content"])
                    analysis["keywords"] = keywords_data.get("keywords", [])
                    analysis["categories"] = keywords_data.get("categories", [])
                except:
                    # 如果JSON解析失败，使用简单关键词
                    words = content.split()
                    analysis["keywords"] = list(set([word for word in words if len(word) > 1]))[:10]
                    analysis["categories"] = []
            else:
                analysis["keywords"] = ["文档", "处理", "分析"]
                analysis["categories"] = []
                analysis["keywords_error"] = keywords_result.get("error", "未知错误")

            # 文档复杂度分析
            analysis["complexity"] = (
                "high" if word_count > 500 else
                "medium" if word_count > 200 else
                "low"
            )

            return analysis

        except Exception as e:
            # 出错时的降级处理
            word_count = len(content.split())
            sentences = content.count('.') + content.count('!') + content.count('?')

            return {
                "sentiment": "neutral",
                "sentiment_confidence": 0.5,
                "complexity": "high" if word_count > 500 else "medium" if word_count > 200 else "low",
                "keywords": ["文档", "处理", "分析"],
                "categories": [],
                "summary": content[:100] + "..." if len(content) > 100 else content,
                "stats": {
                    "word_count": word_count,
                    "sentence_count": sentences,
                    "avg_sentence_length": word_count / sentences if sentences > 0 else 0
                },
                "fallback_mode": True,
                "error": str(e)
            }


# 函数式装饰器示例
def validate_content(func: Callable) -> Callable:
    """内容验证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 假设第一个参数是content
        if args and isinstance(args[1], str):
            content = args[1]
            if not content.strip():
                raise ValueError("文档内容不能为空")
            if len(content) > 100000:
                raise ValueError("文档内容过长，超过100000字符")

        return func(*args, **kwargs)
    return wrapper


def rate_limit(max_requests: int = 10, time_window: int = 60) -> Callable:
    """速率限制装饰器"""
    requests = []

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # 清理过期的请求记录
            requests[:] = [req_time for req_time in requests if now - req_time < time_window]

            if len(requests) >= max_requests:
                raise Exception(f"速率限制: {time_window}秒内最多{max_requests}个请求")

            requests.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# 装饰器模式完整演示
# ============================================================================

def demo_decorator_pattern():
    """
    装饰器模式完整演示

    这个演示展示了装饰器模式的完整工作流程：
    1. 创建基础处理器（Component）
    2. 逐层添加装饰器（Concrete Decorators）
    3. 展示装饰器链的执行过程
    4. 展示AI功能的JSON返回结果
    """
    print("🎭 [装饰器模式演示] ================ 装饰器模式完整演示 ================")
    print("📚 [设计模式] 装饰器模式 (Decorator Pattern)")
    print("💡 [核心理念] 动态地为对象添加新功能，无需修改其代码结构")
    print("=" * 80)

    # 步骤1: 创建基础处理器（装饰器模式的Component）
    print(f"\n🏭 [步骤1] 创建基础文档处理器 (Component)")
    print("-" * 50)
    base_processor = DocumentProcessor()
    print("✅ [基础处理器] DocumentProcessor 创建完成")

    # 步骤2: 逐层添加装饰器 - 展示装饰器的动态组合能力
    print(f"\n🎭 [步骤2] 逐层添加装饰器 (Concrete Decorators)")
    print("-" * 50)

    # 第一层：AI增强装饰器
    print(f"\n🤖 [装饰层1] 添加AI增强装饰器...")
    ai_enhanced_processor = AIEnhancementDecorator(base_processor)

    # 第二层：重试装饰器
    print(f"🔄 [装饰层2] 添加重试装饰器...")
    retry_processor = RetryDecorator(ai_enhanced_processor, max_retries=2, delay=0.5)

    # 第三层：性能监控装饰器
    print(f"⏱️  [装饰层3] 添加性能监控装饰器...")
    performance_processor = PerformanceMonitorDecorator(retry_processor)

    # 第四层：缓存装饰器
    print(f"💾 [装饰层4] 添加缓存装饰器...")
    cache_processor = CacheDecorator(performance_processor, cache_size=5)

    # 第五层：日志装饰器（最外层）
    print(f"📝 [装饰层5] 添加日志装饰器（最外层）...")
    enhanced_processor = LoggingDecorator(cache_processor)

    print("✅ [装饰器链] 5层装饰器组合完成!")

    # 步骤3: 显示装饰器链结构
    print(f"\n🔗 [步骤3] 装饰器链结构分析")
    print("-" * 50)
    print("📋 [执行顺序] 调用顺序（从外到内）：")
    print("   1️⃣ LoggingDecorator (日志记录)")
    print("   2️⃣ CacheDecorator (缓存检查)")
    print("   3️⃣ PerformanceMonitorDecorator (性能监控)")
    print("   4️⃣ RetryDecorator (重试机制)")
    print("   5️⃣ AIEnhancementDecorator (AI分析)")
    print("   6️⃣ DocumentProcessor (基础处理)")

    # 步骤4: 创建测试文档和上下文
    print(f"\n📄 [步骤4] 创建测试文档和上下文")
    print("-" * 50)

    context = ProcessingContext(
        document_id="demo_doc_001",
        user_id="demo_user_zhang",
        session_id="session_20241201",
        metadata={
            "department": "技术部",
            "project": "AI文档分析系统",
            "priority": "high"
        }
    )

    # 创建测试文档内容
    test_content = """
    智能文档分析系统架构设计

    1. 系统概述
    本系统是一个基于人工智能的文档分析平台，旨在为用户提供智能化的文档处理和分析服务。

    2. 核心功能
    - 智能文本摘要生成
    - 情感分析和观点提取
    - 关键词自动提取
    - 文档分类和标签

    3. 技术架构
    系统采用微服务架构，包含以下核心组件：
    - API网关：负责请求路由和负载均衡
    - 文档处理服务：负责文档解析和预处理
    - AI分析服务：集成DeepSeek大语言模型
    - 缓存服务：提供高性能数据缓存

    4. 部署方案
    系统支持容器化部署，使用Docker和Kubernetes进行服务编排。
    数据库采用分布式集群，确保高可用性和数据一致性。

    5. 总结
    本系统通过先进的人工智能技术，为用户提供高效、准确的文档分析服务，
    具有良好的扩展性和维护性。
    """

    print(f"📋 [文档信息] ID: {context.document_id}")
    print(f"👤 [用户信息] ID: {context.user_id}")
    print(f"📏 [内容统计] 长度: {len(test_content)} 字符, {len(test_content.split())} 单词")
    print(f"🏷️  [元数据] 部门: {context.metadata['department']}, 项目: {context.metadata['project']}")

    # 步骤5: 执行第一次处理（无缓存）
    print(f"\n🚀 [步骤5] 第一次处理（无缓存）")
    print("=" * 60)
    print("📊 [预期行为] 缓存未命中，执行完整处理流程")
    print("🔗 [执行链] 日志->缓存->性能监控->重试->AI分析->基础处理")
    print("=" * 60)

    start_time = time.time()
    result1 = enhanced_processor.process(test_content, context)
    end_time = time.time()
    total_time_1 = end_time - start_time

    print(f"\n📊 [第一次处理] 总耗时: {total_time_1:.3f} 秒")

    # 步骤6: 执行第二次处理（使用缓存）
    print(f"\n🎯 [步骤6] 第二次处理（缓存命中）")
    print("=" * 60)
    print("📊 [预期行为] 缓存命中，跳过AI分析直接返回结果")
    print("🔗 [执行链] 日志->缓存（命中）->返回")
    print("=" * 60)

    start_time = time.time()
    result2 = enhanced_processor.process(test_content, context)
    end_time = time.time()
    total_time_2 = end_time - start_time

    print(f"\n📊 [第二次处理] 总耗时: {total_time_2:.3f} 秒")
    print(f"⚡ [性能提升] 缓存加速: {((total_time_1 - total_time_2) / total_time_1 * 100):.1f}%")

    # 步骤7: 展示详细的统计信息
    print(f"\n📈 [步骤7] 详细统计信息")
    print("=" * 60)

    # 缓存统计
    print(f"💾 [缓存统计]")
    cache_stats = cache_processor.get_cache_stats()
    formatted_cache_stats = json.dumps(cache_stats, indent=2, ensure_ascii=False)
    for line in formatted_cache_stats.split('\n'):
        print(f"   {line}")

    # 性能统计
    print(f"\n⏱️  [性能统计]")
    perf_report = performance_processor.get_performance_report()
    formatted_perf_stats = json.dumps(perf_report, indent=2, ensure_ascii=False)
    for line in formatted_perf_stats.split('\n'):
        print(f"   {line}")

    # AI分析统计
    print(f"\n🤖 [AI分析统计]")
    ai_stats = ai_enhanced_processor.get_ai_stats()
    formatted_ai_stats = json.dumps(ai_stats, indent=2, ensure_ascii=False)
    for line in formatted_ai_stats.split('\n'):
        print(f"   {line}")

    # 日志统计
    print(f"\n📝 [日志统计]")
    log_summary = enhanced_processor.get_log_summary()
    formatted_log_stats = json.dumps(log_summary, indent=2, ensure_ascii=False)
    for line in formatted_log_stats.split('\n'):
        print(f"   {line}")

    # 步骤8: 装饰器模式总结
    print(f"\n🎓 [步骤8] 装饰器模式总结")
    print("=" * 80)
    print("""
🎭 装饰器模式核心要点：

1. 🏭 Component (组件)
   - DocumentProcessor: 定义基础处理接口
   - 所有装饰器和具体组件都实现相同接口

2. 🎭 Decorator (装饰器抽象类)
   - ProcessorDecorator: 持有组件引用，定义装饰器接口
   - 通过委托机制调用被装饰对象

3. 🔧 Concrete Decorator (具体装饰器)
   - LoggingDecorator: 添加日志记录功能
   - CacheDecorator: 添加缓存功能
   - PerformanceMonitorDecorator: 添加性能监控
   - RetryDecorator: 添加重试机制
   - AIEnhancementDecorator: 添加AI分析功能

4. 🔄 动态组合
   - 可以在运行时动态组合装饰器
   - 无需修改现有代码即可添加新功能
   - 装饰器顺序可以灵活调整

5. 📊 透明性
   - 装饰器对客户端透明
   - 装饰后的对象与原始对象接口一致

装饰器模式的优势：
✅ 动态添加功能，无需修改代码
✅ 可以组合多个装饰器实现复杂功能
✅ 符合开闭原则，对扩展开放，对修改封闭
✅ 比继承更灵活，避免类爆炸
✅ 可以在运行时动态添加或移除功能

实际应用场景：
- AI工作流中的功能增强
- Web框架中的中间件
- IO流的增强处理
- GUI组件的功能扩展
- 缓存、日志、权限等横切关注点
""")

    return enhanced_processor


if __name__ == "__main__":
    # 运行装饰器模式完整演示
    enhanced_processor = demo_decorator_pattern()