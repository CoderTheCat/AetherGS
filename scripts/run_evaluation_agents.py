#!/usr/bin/env python
"""
运行 3 个评估 Agent
从理论、代码现实、操作复杂度三个维度评估创新点报告
"""

import subprocess
from pathlib import Path
from datetime import datetime

# 配置
OLLAMA_MODEL = "qwen2.5:latest"
PROMPTS_DIR = Path("e:/Code/LiteGS/prompts")
OUTPUT_DIR = Path("e:/Code/LiteGS/evaluation_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# 读取创新点报告
REPORT_FILE = Path("e:/Code/LiteGS/SCI 一区创新点分析报告_2026.md")
with open(REPORT_FILE, 'r', encoding='utf-8') as f:
    report_content = f.read()

# Agent 配置
AGENTS = [
    {
        "name": "theory_evaluation",
        "prompt_file": "12_theory_evaluation_agent.txt",
        "output_file": "theory_evaluation_report.md",
        "description": "理论合理性评估"
    },
    {
        "name": "code_reality",
        "prompt_file": "13_code_reality_agent.txt",
        "output_file": "code_reality_report.md",
        "description": "代码现实性评估"
    },
    {
        "name": "operation_complexity",
        "prompt_file": "14_operation_complexity_agent.txt",
        "output_file": "operation_complexity_report.md",
        "description": "操作复杂度评估"
    }
]

def run_ollama_evaluation(agent_config):
    """使用 Ollama 运行单个评估 agent"""
    prompt_file = PROMPTS_DIR / agent_config["prompt_file"]
    
    print(f"\n{'='*60}")
    print(f"正在运行：{agent_config['description']}")
    print(f"提示词文件：{prompt_file}")
    print(f"使用模型：{OLLAMA_MODEL}")
    print(f"{'='*60}\n")
    
    # 读取提示词
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    # 添加报告内容
    context = f"""
当前日期：{datetime.now().strftime('%Y-%m-%d')}
评估对象：《LiteGS SCI 1 区创新点分析报告_2026.md》

以下是报告的核心内容摘要：

{report_content[:15000]}  # 限制长度，避免超出上下文

---

请基于以上报告内容，按照提示词文件中的评估框架，进行严格、客观、全面的评估。
既要指出优点，也要充分揭示问题和风险。
"""
    
    full_prompt = context + prompt
    
    # 调用 Ollama
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=full_prompt.encode('utf-8'),
            capture_output=True,
            timeout=600  # 10 分钟超时
        )
        
        if result.returncode == 0:
            output = result.stdout.decode('utf-8')
            
            # 保存结果
            output_file = OUTPUT_DIR / agent_config["output_file"]
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# {agent_config['description']}报告\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**使用模型**: {OLLAMA_MODEL}\n\n")
                f.write(f"---\n\n")
                f.write(output)
            
            print(f"✓ 评估完成，结果保存到：{output_file}")
            return output
        else:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            print(f"✗ Ollama 运行失败：{error_msg}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"✗ 评估超时（>10 分钟）")
        return None
    except Exception as e:
        print(f"✗ 发生错误：{e}")
        return None

def main():
    """主函数"""
    print("="*60)
    print("LiteGS 创新点评估分析")
    print(f"使用 Ollama 模型：{OLLAMA_MODEL}")
    print(f"输出目录：{OUTPUT_DIR}")
    print("="*60)
    
    results = {}
    
    # 依次运行 3 个评估 agent
    for agent in AGENTS:
        output = run_ollama_evaluation(agent)
        if output:
            results[agent["name"]] = output
        else:
            print(f"警告：{agent['description']} 失败，继续下一个...")
    
    # 生成汇总报告
    if results:
        print("\n" + "="*60)
        print("生成汇总报告...")
        print("="*60)
        
        summary_file = OUTPUT_DIR / "comprehensive_evaluation.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# LiteGS 创新点综合评估报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"本报告基于 3 个专业化 Agent 的独立评估，从理论合理性、代码现实性、操作复杂度三个维度，")
            f.write(f"全面评估《LiteGS SCI 1 区创新点分析报告_2026.md》中提出的创新方向。\n\n")
            f.write(f"---\n\n")
            f.write(f"## 目录\n\n")
            
            for agent in AGENTS:
                output_file = agent["output_file"]
                description = agent["description"]
                f.write(f"- [{description}](./{output_file})\n")
            
            f.write(f"\n---\n\n")
            f.write(f"## 各 Agent 评估结果\n\n")
            
            for agent in AGENTS:
                if agent["name"] in results:
                    f.write(f"### {agent['description']}\n\n")
                    f.write(f"详细评估请查看：[{agent['output_file']}](./{agent['output_file']})\n\n")
                    # 提取关键内容（前 2000 字）
                    preview = results[agent["name"]][:2000]
                    f.write(f"**内容预览**：\n\n{preview}...\n\n")
                    f.write(f"[阅读全文](./{agent['output_file']})\n\n")
                    f.write(f"---\n\n")
        
        print(f"✓ 汇总报告保存到：{summary_file}")
        
        # 生成最终建议
        print("\n" + "="*60)
        print("评估完成！")
        print("="*60)
        print(f"\n所有结果已保存到：{OUTPUT_DIR}")
        print(f"\n生成的文件：")
        for agent in AGENTS:
            if agent["name"] in results:
                print(f"  - {agent['output_file']}")
        print(f"  - comprehensive_evaluation.md")
        
        print(f"\n下一步：")
        print(f"1. 阅读综合评估报告：{summary_file}")
        print(f"2. 根据评估结果调整创新方向优先级")
        print(f"3. 更新创新点分析报告")
        
    else:
        print("\n✗ 所有评估均失败，请检查 Ollama 配置")

if __name__ == "__main__":
    main()
