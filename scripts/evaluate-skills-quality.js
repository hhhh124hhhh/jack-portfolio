#!/usr/bin/env node

/**
 * 评估生成的 Skills 质量
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const SKILLS_DIR = '/root/clawd/dist/skills';
const OUTPUT_DIR = '/root/clawd/data/skills-evaluation';

/**
 * 解压并读取 SKILL.md
 * @param {string} skillFile - Skill 文件路径
 * @returns {Promise<Object>}
 */
function readSkill(skillFile) {
  return new Promise((resolve, reject) => {
    const tempDir = path.join('/tmp', `skill-eval-${Date.now()}`);
    
    exec(`mkdir -p ${tempDir} && unzip -q "${skillFile}" -d ${tempDir}`, (error) => {
      if (error) {
        reject(error);
        return;
      }

      try {
        const skillMdPath = path.join(tempDir, 'SKILL.md');
        const metadataPath = path.join(tempDir, 'metadata.json');
        
        const skillMd = fs.existsSync(skillMdPath) 
          ? fs.readFileSync(skillMdPath, 'utf8') 
          : '';
        
        const metadata = fs.existsSync(metadataPath)
          ? JSON.parse(fs.readFileSync(metadataPath, 'utf8'))
          : {};

        // 清理临时目录
        exec(`rm -rf ${tempDir}`);

        resolve({
          name: path.basename(skillFile),
          skillMd,
          metadata
        });
      } catch (e) {
        // 清理临时目录
        exec(`rm -rf ${tempDir}`);
        reject(e);
      }
    });
  });
}

/**
 * 提取 Prompt 内容
 * @param {string} skillMd - SKILL.md 内容
 * @returns {string}
 */
function extractPrompt(skillMd) {
  const match = skillMd.match(/## Prompt\s+```\s*(.*?)\s*```/s);
  return match ? match[1].trim() : '';
}

/**
 * 评估 Skill 质量
 * @param {Object} skill - Skill 对象
 * @returns {Object}
 */
function evaluateSkill(skill) {
  const prompt = extractPrompt(skill.skillMd);
  
  // 基础质量指标
  const hasCompletePrompt = prompt.length > 30 && !prompt.includes('...');
  const hasDescription = skill.skillMd.includes('## 描述');
  const hasSource = skill.skillMd.includes('## 来源');
  const hasTags = skill.skillMd.includes('## 标签');
  
  // 提示词质量评估
  let promptQuality = 0;
  
  // 长度适中 (30-200 字符)
  if (prompt.length >= 30 && prompt.length <= 200) {
    promptQuality += 20;
  } else if (prompt.length > 200) {
    promptQuality += 10;
  }
  
  // 包含描述性词汇
  const descriptiveWords = [
    'portrait', 'landscape', 'cinematic', 'natural light', 'style',
    'generate', 'create', 'write', 'act as', 'you are', 'imagine'
  ];
  
  const hasDescriptiveWord = descriptiveWords.some(word =>
    prompt.toLowerCase().includes(word.toLowerCase())
  );
  
  if (hasDescriptiveWord) promptQuality += 20;
  
  // 不包含截断标记
  if (!prompt.includes('...')) promptQuality += 20;
  
  // 句子结构完整（以字母开头，以标点符号结尾）
  const hasCompleteStructure = /^[A-Z]/.test(prompt) && /[.!?]$/.test(prompt);
  if (hasCompleteStructure) promptQuality += 20;
  
  // 不包含无关字符
  if (!prompt.includes(' · ') && !prompt.includes('  ,')) promptQuality += 20;
  
  // 计算综合评分
  let overallScore = 0;
  overallScore += hasCompletePrompt ? 30 : 0;
  overallScore += hasDescription ? 15 : 0;
  overallScore += hasSource ? 15 : 0;
  overallScore += hasTags ? 10 : 0;
  overallScore += (promptQuality / 100) * 30; // Prompt 质量占 30 分
  
  // 评级
  let rating;
  if (overallScore >= 80) {
    rating = 'high';
  } else if (overallScore >= 50) {
    rating = 'medium';
  } else {
    rating = 'low';
  }
  
  return {
    name: skill.name,
    title: skill.metadata.name || skill.name,
    prompt,
    promptLength: prompt.length,
    promptQuality,
    hasCompletePrompt,
    hasDescription,
    hasSource,
    hasTags,
    overallScore: Math.round(overallScore),
    rating
  };
}

/**
 * 主函数
 */
async function main() {
  console.log('='.repeat(80));
  console.log('🔍 评估生成的 Skills 质量');
  console.log('='.repeat(80));
  console.log();
  
  // 确保输出目录存在
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
  
  // 获取所有 .skill 文件（只处理新生成的）
  const files = fs.readdirSync(SKILLS_DIR)
    .filter(f => f.startsWith('image generation-') && f.endsWith('.skill'))
    .sort();
  
  console.log(`找到 ${files.length} 个新生成的 Skills\n`);
  
  const evaluations = [];
  let processed = 0;
  
  for (const file of files) {
    const skillFile = path.join(SKILLS_DIR, file);
    
    try {
      const skill = await readSkill(skillFile);
      const evaluation = evaluateSkill(skill);
      evaluations.push(evaluation);
      
      processed++;
      
      if (processed % 10 === 0) {
        console.log(`已处理: ${processed}/${files.length}`);
      }
    } catch (error) {
      console.error(`✗ 处理失败: ${file} - ${error.message}`);
    }
  }
  
  console.log(`\n✓ 处理完成: ${processed} 个 Skills\n`);
  
  // 按评分排序
  evaluations.sort((a, b) => b.overallScore - a.overallScore);
  
  // 统计
  const highQuality = evaluations.filter(e => e.rating === 'high');
  const mediumQuality = evaluations.filter(e => e.rating === 'medium');
  const lowQuality = evaluations.filter(e => e.rating === 'low');
  
  console.log('='.repeat(80));
  console.log('📊 质量统计');
  console.log('='.repeat(80));
  console.log();
  console.log(`  总计: ${evaluations.length}`);
  console.log(`  高质量 (>=80): ${highQuality.length} (${Math.round(highQuality.length / evaluations.length * 100)}%)`);
  console.log(`  中等质量 (50-79): ${mediumQuality.length} (${Math.round(mediumQuality.length / evaluations.length * 100)}%)`);
  console.log(`  低质量 (<50): ${lowQuality.length} (${Math.round(lowQuality.length / evaluations.length * 100)}%)`);
  console.log();
  
  // 显示高质量 Skills
  console.log('='.repeat(80));
  console.log('🌟 高质量 Skills');
  console.log('='.repeat(80));
  console.log();
  
  for (const eval of highQuality.slice(0, 10)) {
    console.log(`评分: ${eval.overallScore}/100 | ${eval.name}`);
    console.log(`提示词: ${eval.prompt}`);
    console.log();
  }
  
  // 保存评估结果
  const timestamp = new Date().toISOString().split('T')[0];
  const outputFile = path.join(OUTPUT_DIR, `skills-evaluation-${timestamp}.json`);
  
  const report = {
    timestamp: new Date().toISOString(),
    total: evaluations.length,
    highQuality: highQuality.length,
    mediumQuality: mediumQuality.length,
    lowQuality: lowQuality.length,
    evaluations
  };
  
  fs.writeFileSync(outputFile, JSON.stringify(report, null, 2), 'utf8');
  
  console.log('='.repeat(80));
  console.log(`✅ 评估报告已保存: ${outputFile}`);
  console.log('='.repeat(80));
}

main().catch(console.error);
