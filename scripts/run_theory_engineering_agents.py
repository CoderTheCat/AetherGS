#!/usr/bin/env python
"""
运行 3 个理论 - 工程协同分析 Agent
分析理论创新与工程创新的兼容性、协同效应和集成架构
"""

import subprocess
from pathlib import Path
from datetime import datetime

# 配置
OLLAMA_MODEL = "qwen2.5:latest"
PROMPTS_DIR = Path("e:/Code/LiteGS/prompts")
OUTPUT_DIR = Path("e:/Code/LiteGS/theory_engineering_analysis")
OUTPUT_DIR.mkdir(exist_ok=True)

# 读取创新点报告
REPORT_FILE = Path("e:/Code/LiteGS/SCI 一区创新点分析报告_2026.md")
with open(REPORT_FILE, 'r', encoding='utf-8') as f:
    report_content = f.read()

# Agent 配置
AGENTS = [
    {
        "name": "theory_engineering_compatibility",
        "prompt_file": "15_theory_engineering_compatibility_agent.txt",
        "output_file": "compatibility_analysis.md",
        "description": "理论 - 工程兼容性分析"
    },
    {
        "name": "performance_theory_synergy",
        "prompt_file": "16_performance_theory_synergy_agent.txt",
        "output_file": "synergy_analysis.md",
        "description": "性能 - 理论协同分析"
    },
    {
        "name": "architecture_integration",
        "prompt_file": "17_architecture_integration_agent.txt",
        "output_file": "architecture_design.md",
        "description": "架构集成设计"
    }
]

def run_ollama_analysis(agent_config):
    """使用 Ollama 运行单个分析 agent"""
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
分析目标：将理论创新与工程创新有机结合，实现理论深度与工程性能的双重卓越

创新点报告内容：
{report_content[:15000]}  # 限制长度

---

请基于以上报告内容，按照提示词文件中的分析框架，进行深入分析。
重点关注：
1. 理论方向与工程方向的协同效应
2. 如何将理论洞察转化为实际性能提升
3. 代码架构如何支持理论 - 工程一体化

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
            
            print(f"✓ 分析完成，结果保存到：{output_file}")
            return output
        else:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            print(f"✗ Ollama 运行失败：{error_msg}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"✗ 分析超时（>10 分钟）")
        return None
    except Exception as e:
        print(f"✗ 发生错误：{e}")
        return None

def main():
    """主函数"""
    print("="*60)
    print("LiteGS 理论 - 工程协同分析")
    print(f"使用 Ollama 模型：{OLLAMA_MODEL}")
    print(f"输出目录：{OUTPUT_DIR}")
    print("="*60)
    
    results = {}
    
    # 依次运行 3 个分析 agent
    for agent in AGENTS:
        output = run_ollama_analysis(agent)
        if output:
            results[agent["name"]] = output
        else:
            print(f"警告：{agent['description']} 失败，继续下一个...")
    
    # 生成汇总报告
    if results:
        print("\n" + "="*60)
        print("生成汇总报告...")
        print("="*60)
        
        summary_file = OUTPUT_DIR / "theory_engineering_integration.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# LiteGS 理论 - 工程一体化集成报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"本报告基于 3 个专业化 Agent 的独立分析，全面研究如何将理论创新与工程创新有机结合，")
            f.write(f"实现理论深度与工程性能的双重卓越。\n\n")
            f.write(f"---\n\n")
            f.write(f"## 目录\n\n")
            
            for agent in AGENTS:
                output_file = agent["output_file"]
                description = agent["description"]
                f.write(f"- [{description}](./{output_file})\n")
            
            f.write(f"\n---\n\n")
            f.write(f"## 各 Agent 分析结果\n\n")
            
            for agent in AGENTS:
                if agent["name"] in results:
                    f.write(f"### {agent['description']}\n\n")
                    f.write(f"详细分析请查看：[{agent['output_file']}](./{agent['output_file']})\n\n")
                    # 提取关键内容（前 2000 字）
                    preview = results[agent["name"]][:2000]
                    f.write(f"**内容预览**：\n\n{preview}...\n\n")
                    f.write(f"[阅读全文](./{agent['output_file']})\n\n")
                    f.write(f"---\n\n")
        
        print(f"✓ 汇总报告保存到：{summary_file}")
        
        # 生成最终建议
        print("\n" + "="*60)
        print("分析完成！")
        print("="*60)
        print(f"\n所有结果已保存到：{OUTPUT_DIR}")
        print(f"\n生成的文件：")
        for agent in AGENTS:
            if agent["name"] in results:
                print(f"  - {agent['output_file']}")
        print(f"  - theory_engineering_integration.md")
        
        print(f"\n下一步：")
        print(f"1. 阅读理论 - 工程一体化集成报告：{summary_file}")
        print(f"2. 根据协同效应分析选择最佳组合")
        print(f"3. 按照架构设计实现集成")
        print(f"4. 更新项目创新点文档和代码架构")
        
    else:
        print("\n✗ 所有分析均失败，请检查 Ollama 配置")

if __name__ == "__main__":
    main()
