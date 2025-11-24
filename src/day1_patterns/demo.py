"""
AI工作流中的设计模式综合演示

本文件展示了如何在AI工作流中使用策略模式、装饰器模式和责任链模式
来处理长文档，以及如何组合这些模式实现更强大的功能。
"""

import time
from typing import Dict, Any, List
from dataclasses import dataclass

# 导入三种模式的实现
from strategy import Document, DocumentProcessor, LegalDocumentStrategy, TechnicalDocumentStrategy
from decorator import ProcessingContext, LoggingDecorator, CacheDecorator, PerformanceMonitorDecorator
from responsibility_chain import ProcessingRequest, ProcessingChainBuilder


@dataclass
class DocumentProcessingJob:
    """文档处理任务"""
    document: Document
    context: ProcessingContext
    use_strategies: bool = True
    use_decorators: bool = True
    use_chain: bool = True


class IntegratedDocumentProcessor:
    """集成的文档处理器 - 组合三种设计模式"""

    def __init__(self):
        # 初始化策略模式的处理器
        self.strategy_processor = DocumentProcessor()

        # 初始化装饰器模式的处理器
        base_processor = DocumentProcessor()
        self.decorated_processor = LoggingDecorator(
            CacheDecorator(
                PerformanceMonitorDecorator(base_processor)
            )
        )

        # 初始化责任链模式
        self.chain_processor = ProcessingChainBuilder().create_default_chain()

    def process_document(self, job: DocumentProcessingJob) -> Dict[str, Any]:
        """使用不同模式处理文档"""
        results = {
            "job_id": f"job_{int(time.time())}",
            "document_title": job.document.title,
            "processing_modes": [],
            "results": {}
        }

        print(f"🎯 开始综合处理: {job.document.title}")
        print("=" * 60)

        # 1. 策略模式处理
        if job.use_strategies:
            print("\n1️⃣ 策略模式处理")
            print("-" * 30)
            strategy_result = self.strategy_processor.process_document(job.document)
            results["processing_modes"].append("strategy")
            results["results"]["strategy"] = strategy_result

        # 2. 装饰器模式处理
        if job.use_decorators:
            print("\n2️⃣ 装饰器模式处理")
            print("-" * 30)
            decorator_result = self.decorated_processor.process(job.document.content, job.context)
            results["processing_modes"].append("decorator")
            results["results"]["decorator"] = decorator_result

        # 3. 责任链模式处理
        if job.use_chain:
            print("\n3️⃣ 责任链模式处理")
            print("-" * 30)
            chain_request = ProcessingRequest(
                content=job.document.content,
                metadata={
                    "format": "markdown",
                    "document_type": job.document.doc_type,
                    "title": job.document.title,
                    **job.context.metadata
                }
            )
            chain_result = self.chain_processor.process(chain_request)
            results["processing_modes"].append("chain")
            results["results"]["chain"] = chain_request.results

        print("\n✅ 综合处理完成!")
        return results


def create_sample_documents() -> List[Document]:
    """创建示例文档集合"""

    # 法律文档
    legal_doc = Document(
        content="""
        # 软件许可协议

        第一条 许可授予
        本公司（以下简称"许可方"）特此授予您（以下简称"被许可方"）使用本软件的非独占性许可。

        第二条 使用限制
        1. 被许可方不得对软件进行反向工程、反编译或反汇编。
        2. 被许可方不得将软件用于商业目的，除非获得许可方的书面同意。
        3. 被许可方应在软件的所有副本中保留版权声明。

        第三条 知识产权
        软件的所有知识产权归许可方所有。被许可方获得的使用许可并不转让任何知识产权。

        第四条 免责声明
        本软件按"现状"提供，不提供任何明示或暗示的保证。
        """,
        title="软件许可协议",
        doc_type="legal"
    )

    # 技术文档
    tech_doc = Document(
        content="""
        # 微服务架构设计文档

        ## 系统概述

        本系统采用微服务架构，包含以下核心服务：
        - 用户服务 (User Service)
        - 订单服务 (Order Service)
        - 支付服务 (Payment Service)
        - 库存服务 (Inventory Service)

        ## API设计

        ### 用户服务 API
        - GET /api/users - 获取用户列表
        - POST /api/users - 创建新用户
        - GET /api/users/{id} - 获取用户详情
        - PUT /api/users/{id} - 更新用户信息
        - DELETE /api/users/{id} - 删除用户

        ### 数据模型
        用户实体包含以下字段：
        ```json
        {
          "id": "string",
          "username": "string",
          "email": "string",
          "created_at": "datetime",
          "updated_at": "datetime"
        }
        ```

        ## 部署架构

        系统部署在Kubernetes集群中，使用Docker容器化。
        服务之间通过REST API进行通信，使用Redis作为缓存。
        数据库采用MySQL集群，实现高可用性。
        """,
        title="微服务架构设计",
        doc_type="technical"
    )

    # 学术文档
    academic_doc = Document(
        content="""
        # 基于深度学习的自然语言处理研究

        ## 摘要

        本研究提出了一种新的深度学习模型，用于改进自然语言处理任务的性能。
        通过引入注意力机制和预训练技术，我们的模型在多个基准测试中取得了最先进的结果。

        ## 1. 引言

        自然语言处理（NLP）是人工智能领域的重要研究方向。近年来，随着深度学习技术的发展，
        NLP任务取得了显著进展。然而，现有的模型在处理长文本和理解上下文方面仍存在挑战。

        ## 2. 相关工作

        Smith等人(2020)提出了Transformer模型，彻底改变了NLP领域。
        Jones等人(2021)进一步改进了注意力机制，提高了模型性能。
        Brown等人(2022)开发了大规模语言模型GPT-3，展示了令人印象深刻的能力。

        ## 3. 方法

        ### 3.1 模型架构
        我们提出了一种新的神经网络架构，结合了CNN和RNN的优点。
        模型包含以下组件：
        - 嵌入层：将词向量转换为高维表示
        - 注意力层：捕获长距离依赖关系
        - 前馈网络层：非线性变换

        ### 3.2 训练策略
        我们使用预训练+微调的策略：
        1. 在大规模语料库上进行预训练
        2. 在特定任务上进行微调

        ## 4. 实验结果

        在GLUE基准测试中，我们的模型达到了平均91.2%的准确率，
        超过了之前最好的模型2.3个百分点。
        """,
        title="深度学习NLP研究论文",
        doc_type="academic"
    )

    return [legal_doc, tech_doc, academic_doc]


def demonstrate_design_patterns():
    """演示三种设计模式的使用"""
    print("🎓 AI工作流中的设计模式演示")
    print("=" * 80)
    print("本演示展示如何在AI工作流中使用策略模式、装饰器模式和责任链模式处理长文档")
    print("=" * 80)

    # 创建集成处理器
    processor = IntegratedDocumentProcessor()

    # 创建示例文档
    documents = create_sample_documents()

    # 处理每个文档
    for i, doc in enumerate(documents, 1):
        print(f"\n📄 文档 {i}: {doc.title}")
        print(f"类型: {doc.doc_type}, 长度: {doc.length} 字符")

        # 创建处理任务
        job = DocumentProcessingJob(
            document=doc,
            context=ProcessingContext(
                document_id=f"doc_{i:03d}",
                user_id="demo_user",
                metadata={"demo_mode": True}
            ),
            use_strategies=True,
            use_decorators=True,
            use_chain=True
        )

        # 处理文档
        result = processor.process_document(job)

        # 显示处理摘要
        print(f"\n📊 处理摘要:")
        print(f"  任务ID: {result['job_id']}")
        print(f"  使用模式: {', '.join(result['processing_modes'])}")

        if 'strategy' in result['results']:
            strategy_result = result['results']['strategy']
            print(f"  策略模式: 使用 {strategy_result['strategy']} 策略，处理了 {strategy_result['total_chunks']} 个片段")

        if 'decorator' in result['results']:
            decorator_result = result['results']['decorator']
            if 'performance' in decorator_result:
                perf = decorator_result['performance']
                print(f"  装饰器模式: 处理时间 {perf['processing_time']:.3f}s")

        if 'chain' in result['results']:
            chain_result = result['results']['chain']
            if 'final_output' in chain_result:
                summary = chain_result['final_output']['summary']
                print(f"  责任链模式: 质量 {summary['quality_score']:.2f}, 情感 {summary['sentiment']}")

        print("\n" + "=" * 80)


def demonstrate_pattern_combinations():
    """演示模式组合的高级用法"""
    print("\n\n🔗 模式组合高级演示")
    print("=" * 80)

    # 展示如何在实际应用中组合使用这些模式

    print("""
    💡 设计模式组合策略:

    1️⃣ 策略模式 + 责任链模式:
       - 使用策略模式选择不同的文档处理策略
       - 在每种策略内部使用责任链模式处理具体的分析步骤
       - 优势: 灵活的文档类型适应 + 模块化的处理流程

    2️⃣ 装饰器模式 + 责任链模式:
       - 使用装饰器为整个处理链添加横切关注点
       - 如缓存、日志、性能监控等
       - 优势: 不修改处理链逻辑的情况下添加通用功能

    3️⃣ 三种模式组合:
       - 策略模式: 根据文档类型选择高层处理策略
       - 责任链模式: 在策略内部执行具体的处理步骤
       - 装饰器模式: 为整个处理过程添加增强功能
    """)

    print("\n🏗️ 实际应用场景:")
    print("""
    场景1: 企业文档分析系统
    - 策略模式: 处理不同类型的业务文档（合同、报告、邮件）
    - 责任链模式: 统一的分析流程（格式检查→内容提取→风险识别）
    - 装饰器模式: 审计日志、权限检查、结果缓存

    场景2: 智能客服系统
    - 策略模式: 不同类型问题的处理策略（咨询、投诉、技术支持）
    - 责任链模式: 问题理解→意图识别→答案生成→质量检查
    - 装饰器模式: 对话记录、性能监控、个性化推荐

    场景3: 内容审核平台
    - 策略模式: 不同内容格式的审核策略（文本、图片、视频）
    - 责任链模式: 合规检查→内容分类→风险评分
    - 装饰器模式: 审核记录、人工审核接口、申诉处理
    """)


if __name__ == "__main__":
    # 运行演示
    demonstrate_design_patterns()
    demonstrate_pattern_combinations()

    print("\n\n🎉 演示完成!")
    print("您已经了解了如何在AI工作流中使用三种重要的设计模式来处理长文档。")
    print("这些模式可以单独使用，也可以组合使用，以构建灵活、可扩展的AI系统。")