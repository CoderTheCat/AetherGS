#!/usr/bin/env python
"""
运行 4 个创新点分析 Agent
使用本地 Ollama 模型执行深度分析
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

# 配置
OLLAMA_MODEL = "qwen2.5:latest"  # 或 "llama3:latest"
PROMPTS_DIR = Path("e:/Code/LiteGS/prompts")
OUTPUT_DIR = Path("e:/Code/LiteGS/analysis_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# Agent 配置
AGENTS = [
    {
        "name": "theory_innovation",
        "prompt_file": "08_theory_innovation_agent.txt",
        "output_file": "theory_innovation_analysis.md",
        "description": "理论创新分析"
    },
    {
        "name": "code_implementation",
        "prompt_file": "09_code_implementation_agent.txt",
        "output_file": "code_implementation_analysis.md",
        "description": "代码实现分析"
    },
    {
        "name": "lessons_learned",
        "prompt_file": "10_lessons_learned_agent.txt",
        "output_file": "lessons_learned_analysis.md",
        "description": "经验教训分析"
    },
    {
        "name": "engineering_practice",
        "prompt_file": "11_engineering_practice_agent.txt",
        "output_file": "engineering_practice_analysis.md",
        "description": "工程实际分析"
    }
]

def run_ollama_analysis(agent_config):
    """使用 Ollama 运行单个 agent 分析"""
    prompt_file = PROMPTS_DIR / agent_config["prompt_file"]
    
    print(f"\n{'='*60}")
    print(f"正在运行：{agent_config['description']}")
    print(f"提示词文件：{prompt_file}")
    print(f"使用模型：{OLLAMA_MODEL}")
    print(f"{'='*60}\n")
    
    # 读取提示词
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    # 添加上下文信息
    context = f"""
当前日期：{datetime.now().strftime('%Y-%m-%d')}
项目：LiteGS (3D Gaussian Splatting 加速版本)
现有特性：全链路加速、Warp 光栅化、聚类剔除、压缩流水线
目标：生成 SCI 1 区论文级别的创新点

"""
    
    full_prompt = context + prompt
    
    # 调用 Ollama
    try:
        # 使用 stdin 传递 prompt，避免命令行参数编码问题
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
    print("LiteGS SCI 1 区创新点分析")
    print(f"使用 Ollama 模型：{OLLAMA_MODEL}")
    print(f"输出目录：{OUTPUT_DIR}")
    print("="*60)
    
    results = {}
    
    # 依次运行 4 个 agent
    for agent in AGENTS:
        output = run_ollama_analysis(agent)
        if output:
            results[agent["name"]] = output
        else:
            print(f"警告：{agent['description']} 分析失败，继续下一个...")
    
    # 生成汇总报告
    if results:
        print("\n" + "="*60)
        print("生成汇总报告...")
        print("="*60)
        
        summary_file = OUTPUT_DIR / "innovation_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# LiteGS SCI 1 区创新点分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"本报告基于 4 个专业化 Agent 的独立分析，从理论、代码实现、经验教训和工程实践四个维度，")
            f.write(f"全面分析了 LiteGS 项目可以实现哪些 SCI 1 区级别的创新点。\n\n")
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
        print(f"  - innovation_summary.md")
        
        print(f"\n下一步：")
        print(f"1. 阅读汇总报告：{summary_file}")
        print(f"2. 根据推荐优先级选择创新方向")
        print(f"3. 更新项目创新点文档")
        
    else:
        print("\n✗ 所有分析均失败，请检查 Ollama 配置")

if __name__ == "__main__":
    main()
