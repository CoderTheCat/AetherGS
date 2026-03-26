#!/bin/bash
# C 类创新点 1000 迭代快速测试执行脚本（WSL2 版本）
# 使用方法：./scripts/benchmark/run_c_class_tests_wsl2.sh

set -e

echo "============================================================"
echo "C 类创新点 1000 迭代快速测试（WSL2 环境）"
echo "============================================================"
echo "开始时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "数据集：/mnt/e/Code/LiteGS/data/360_v2/garden"
echo "迭代次数：1000"
echo "============================================================"
echo ""

# 创建结果目录
RESULTS_DIR="results"
mkdir -p $RESULTS_DIR

# 时间戳
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# 测试列表
declare -a TESTS=(
    "渐进式密度控制-Baseline:scripts/benchmark/progressive_densify_1000iter.py:--baseline --output $RESULTS_DIR/baseline_progressive_${TIMESTAMP}.json"
    "渐进式密度控制 - 实验组:scripts/benchmark/progressive_densify_1000iter.py:--output $RESULTS_DIR/progressive_${TIMESTAMP}.json"
    "FP8 混合精度-Baseline:scripts/benchmark/fp8_mixed_precision_1000iter.py:--baseline --output $RESULTS_DIR/baseline_fp8_${TIMESTAMP}.json"
    "FP8 混合精度 - 实验组:scripts/benchmark/fp8_mixed_precision_1000iter.py:--output $RESULTS_DIR/fp8_${TIMESTAMP}.json"
    "视锥剔除增强-Baseline:scripts/benchmark/frustum_culling_enhanced_1000iter.py:--baseline --output $RESULTS_DIR/baseline_culling_${TIMESTAMP}.json"
    "视锥剔除增强 - 实验组:scripts/benchmark/frustum_culling_enhanced_1000iter.py:--output $RESULTS_DIR/enhanced_culling_${TIMESTAMP}.json"
)

# 结果数组
declare -a RESULTS=()

# 运行测试
for test_info in "${TESTS[@]}"; do
    IFS=':' read -r name script args <<< "$test_info"
    
    echo ""
    echo "============================================================"
    echo "运行：$name"
    echo "============================================================"
    echo "命令：python $script $args"
    echo ""
    
    if python $script $args; then
        echo "✅ 测试完成：$name"
        RESULTS+=("✅ $name")
    else
        echo "❌ 测试失败：$name"
        RESULTS+=("❌ $name")
    fi
done

# 打印总结
echo ""
echo "============================================================"
echo "测试总结"
echo "============================================================"
for result in "${RESULTS[@]}"; do
    echo "$result"
done

echo ""
echo "结束时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# 生成测试报告
REPORT_FILE="$RESULTS_DIR/test_summary_${TIMESTAMP}.txt"
{
    echo "C 类创新点 1000 迭代快速测试报告"
    echo "============================================================"
    echo "开始时间：$(date '+%Y-%m-%d %H:%M:%S')"
    echo "数据集：/mnt/e/Code/LiteGS/data/360_v2/garden"
    echo "迭代次数：1000"
    echo "============================================================"
    echo ""
    for result in "${RESULTS[@]}"; do
        echo "$result"
    done
    echo ""
    echo "结束时间：$(date '+%Y-%m-%d %H:%M:%S')"
} > $REPORT_FILE

echo ""
echo "测试报告已保存到：$REPORT_FILE"
echo ""
echo "下一步：使用 analyze_c_class_results.py 分析测试结果"
echo "示例："
echo "  python scripts/analyze/analyze_c_class_results.py \\"
echo "    --baseline results/baseline_progressive_${TIMESTAMP}.json \\"
echo "    --experimental results/progressive_${TIMESTAMP}.json \\"
echo "    --innovation progressive_densify \\"
echo "    --scene garden \\"
echo "    --output results/analysis/"
