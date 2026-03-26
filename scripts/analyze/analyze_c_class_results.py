#!/usr/bin/env python
"""
C 类创新点测试结果分析脚本

功能：
1. 读取多个测试结果 JSON 文件
2. 对比实验组和 baseline 的性能指标
3. 生成对比表格和可视化图表
4. 输出分析报告
"""

import json
import os
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def load_results(file_path):
    """加载测试结果 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_results(baseline_file, experimental_file):
    """对比 baseline 和实验组结果"""
    baseline = load_results(baseline_file)
    experimental = load_results(experimental_file)
    
    comparison = {
        'baseline': baseline,
        'experimental': experimental,
        'improvements': {}
    }
    
    # 计算性能提升
    if 'training_time_seconds' in baseline and 'training_time_seconds' in experimental:
        baseline_time = baseline['training_time_seconds']
        exp_time = experimental['training_time_seconds']
        speedup = (baseline_time - exp_time) / baseline_time * 100
        comparison['improvements']['training_speed'] = {
            'baseline': baseline_time,
            'experimental': exp_time,
            'improvement_percent': speedup
        }
    
    if 'avg_iter_time_ms' in baseline and 'avg_iter_time_ms' in experimental:
        baseline_iter = baseline['avg_iter_time_ms']
        exp_iter = experimental['avg_iter_time_ms']
        iter_improvement = (baseline_iter - exp_iter) / baseline_iter * 100
        comparison['improvements']['avg_iter_time'] = {
            'baseline': baseline_iter,
            'experimental': exp_iter,
            'improvement_percent': iter_improvement
        }
    
    return comparison

def generate_report(comparison, innovation_name, scene):
    """生成测试报告"""
    report = []
    report.append("=" * 60)
    report.append(f"C 类创新点性能测试报告")
    report.append("=" * 60)
    report.append(f"创新点：{innovation_name}")
    report.append(f"测试场景：{scene}")
    report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 训练速度对比
    if 'training_speed' in comparison['improvements']:
        speed = comparison['improvements']['training_speed']
        report.append("训练速度对比:")
        report.append(f"  Baseline: {speed['baseline']:.2f} 秒")
        report.append(f"  实验组：{speed['experimental']:.2f} 秒")
        report.append(f"  提升：{speed['improvement_percent']:.2f}%")
        report.append("")
    
    # 平均迭代时间对比
    if 'avg_iter_time' in comparison['improvements']:
        iter_time = comparison['improvements']['avg_iter_time']
        report.append("平均迭代时间对比:")
        report.append(f"  Baseline: {iter_time['baseline']:.2f} ms/iter")
        report.append(f"  实验组：{iter_time['experimental']:.2f} ms/iter")
        report.append(f"  提升：{iter_time['improvement_percent']:.2f}%")
        report.append("")
    
    # 综合评价
    report.append("综合评价:")
    if 'training_speed' in comparison['improvements']:
        speedup = comparison['improvements']['training_speed']['improvement_percent']
        if speedup >= 30:
            report.append(f"  ✅ 性能提升显著 ({speedup:.2f}%)")
        elif speedup >= 20:
            report.append(f"  ✅ 性能提升良好 ({speedup:.2f}%)")
        elif speedup >= 10:
            report.append(f"  ⚠️  性能有一定提升 ({speedup:.2f}%)")
        else:
            report.append(f"  ❌ 性能提升不明显 ({speedup:.2f}%)")
    
    report.append("")
    report.append("=" * 60)
    
    return "\n".join(report)

def plot_comparison(comparison, output_file, innovation_name):
    """生成对比图表"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 训练速度对比
    if 'training_speed' in comparison['improvements']:
        speed = comparison['improvements']['training_speed']
        labels = ['Baseline', innovation_name]
        values = [speed['baseline'], speed['experimental']]
        colors = ['#ff6b6b', '#4ecdc4']
        
        bars = ax.bar(labels, values, color=colors, alpha=0.7)
        ax.set_ylabel('训练时间 (秒)')
        ax.set_title(f'{innovation_name} - 训练速度对比')
        
        # 在柱子上添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2f}s',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150)
        plt.close()
        print(f"图表已保存到：{output_file}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="C 类创新点测试结果分析")
    parser.add_argument("--baseline", type=str, required=True, help="Baseline 结果文件")
    parser.add_argument("--experimental", type=str, required=True, help="实验组结果文件")
    parser.add_argument("--innovation", type=str, required=True, help="创新点名称")
    parser.add_argument("--scene", type=str, default="garden", help="测试场景")
    parser.add_argument("--output", type=str, default="results", help="输出目录")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.baseline):
        print(f"错误：Baseline 文件不存在：{args.baseline}")
        return
    
    if not os.path.exists(args.experimental):
        print(f"错误：实验组文件不存在：{args.experimental}")
        return
    
    # 对比结果
    print("正在加载和对比结果...")
    comparison = compare_results(args.baseline, args.experimental)
    
    # 生成报告
    report = generate_report(comparison, args.innovation, args.scene)
    print("\n" + report)
    
    # 保存报告
    report_file = os.path.join(args.output, f"{args.innovation}_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存到：{report_file}")
    
    # 生成图表
    chart_file = os.path.join(args.output, f"{args.innovation}_comparison.png")
    plot_comparison(comparison, chart_file, args.innovation)
    
    # 生成 JSON 格式的对比结果
    json_file = os.path.join(args.output, f"{args.innovation}_comparison.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    print(f"JSON 结果已保存到：{json_file}")

if __name__ == "__main__":
    main()
