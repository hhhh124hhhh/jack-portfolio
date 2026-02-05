#!/usr/bin/env python3
"""
生成谷歌生图模型和 Sora 2 的示例 Prompts 并转换为 Skills
"""

import json
import os
from datetime import datetime
import hashlib

# 配置
OUTPUT_DIR = "/root/clawd/generated-skills"
PACKAGES_OUTPUT_DIR = "/root/clawd/dist/skills"

# 创建目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PACKAGES_OUTPUT_DIR, exist_ok=True)

# 谷歌生图模型示例 Prompts
GOOGLE_IMAGE_PROMPTS = [
    {
        "name": "Google Imagen 3 - 超写实风景",
        "description": "使用 Google Imagen 3 生成超写实的风景照片",
        "prompt": """A breathtaking landscape photograph captured during golden hour, shot on Google Imagen 3 with 8K resolution. The scene features rolling hills covered in wildflowers under dramatic orange and purple sky with soft clouds. In the foreground, a crystal-clear lake reflects the mountains, creating a perfect mirror image. The lighting is warm and magical, with natural shadows adding depth and dimension. The composition follows the rule of thirds, with the horizon line placed slightly below center. The style is hyperrealistic with rich colors, fine details, and natural textures. The image should have depth of field, with the foreground flowers in sharp focus and the distant mountains slightly blurred. The mood is peaceful and awe-inspiring, evoking a sense of tranquility and wonder. The overall aesthetic is similar to National Geographic photography, with vibrant colors, sharp details, and natural lighting. No people or buildings in frame, just pure nature at its most beautiful.""",
        "type": "谷歌生图",
        "quality": 95
    },
    {
        "name": "Google Veo - 动态城市夜景",
        "description": "使用 Google Veo 生成动态城市夜景视频",
        "prompt": """Create a stunning nighttime cityscape video using Google Veo, featuring a futuristic metropolis with towering skyscrapers covered in LED lights. The camera movement is smooth and cinematic, starting with a wide shot of the city skyline, then slowly panning down to street level where neon signs and holographic advertisements light up the dark streets. The video quality should be 4K with 60fps, smooth motion, and cinematic color grading. The lighting should be dramatic and atmospheric, with warm streetlights contrasting against the cool blue of the night sky. The city should look alive and vibrant, with cars moving on streets, people walking on sidewalks, and holographic displays projecting advertisements on building facades. The overall mood is futuristic and exciting, evoking a sense of wonder and technological advancement. The video should be rendered with realistic physics, natural movements, and high-quality textures. The style should be similar to Blade Runner 2049, with neon lights, holographic elements, and a dense urban environment.""",
        "type": "谷歌生图",
        "quality": 90
    },
    {
        "name": "Google Imagen 3 - 人像摄影",
        "description": "使用 Google Imagen 3 生成专业人像摄影",
        "prompt": """A professional portrait photography captured on Google Imagen 3, featuring a young woman with warm, natural lighting. The subject is looking directly at the camera with a soft, confident expression. Her hair is styled in loose waves, catching the warm golden hour light. The background is a soft-focus garden with blurred flowers and greenery, creating a natural and pleasant atmosphere. The lighting is warm and flattering, with soft shadows adding depth to her features. The image is captured with a shallow depth of field, keeping her eyes and face in sharp focus while the background is pleasantly blurred. The colors are natural and vibrant, with her skin tone looking healthy and natural. The overall style is similar to professional portrait photography, with careful attention to lighting, composition, and subject expression. The image should be rendered in 8K resolution with fine details, natural textures, and professional color grading. The mood is warm, confident, and approachable, evoking a sense of trust and professionalism.""",
        "type": "谷歌生图",
        "quality": 92
    }
]

# Sora 2 示例 Prompts
SORA2_PROMPTS = [
    {
        "name": "Sora 2 - 超级英雄电影",
        "description": "使用 Sora 2 生成高质量超级英雄电影场景",
        "prompt": """Create an epic superhero movie scene using OpenAI Sora 2, featuring a powerful hero with incredible abilities. The scene begins with a wide shot of a city under attack, with buildings on fire and citizens fleeing in panic. The hero, wearing a sleek high-tech suit with glowing blue energy lines, descends from the sky, creating a shockwave that extinguishes fires and stops falling debris. The camera follows the hero as they fight through waves of enemies, showcasing their superhuman strength, speed, and energy projection abilities. The action is fast-paced and dynamic, with the hero effortlessly defeating enemies using a combination of martial arts and energy projection. The scene culminates with a dramatic final battle against the main villain, with the hero unleashing a massive energy blast that engulfs the entire city in a brilliant explosion of blue light. The video quality should be 4K with 60fps, with smooth motion, realistic physics, and stunning visual effects. The style should be similar to Marvel Cinematic Universe, with epic scale, dynamic action, and high-quality visual effects. The overall mood is heroic and inspiring, evoking a sense of power and hope.""",
        "type": "Sora 2",
        "quality": 95
    },
    {
        "name": "Sora 2 - 自然纪录片",
        "description": "使用 Sora 2 生成高质量自然纪录片",
        "prompt": """Create a stunning nature documentary video using OpenAI Sora 2, featuring incredible wildlife and landscapes. The video begins with a sweeping aerial shot of a pristine rainforest at dawn, with mist rising through the canopy and sunlight filtering through leaves. The camera then follows a majestic jaguar as it stalks through the forest, showcasing its power and grace. The jaguar encounters a family of capuchin monkeys in the trees, creating a moment of interplay between predator and prey. The scene transitions to a beautiful waterfall with toucans and macaws flying in the mist, creating a colorful and vibrant display of tropical life. The video then shifts to a river with caimans and giant river otters playing, showcasing the rich biodiversity of the Amazon rainforest. The entire video is narrated with a warm and educational voiceover, explaining the importance of conservation and the interconnectedness of all species. The video quality should be 4K with 60fps, with stunning cinematography and vibrant, natural colors. The style should be similar to BBC Planet Earth, with breathtaking visuals, smooth camera movements, and educational value. The overall mood is inspiring and educational, evoking a sense of wonder and appreciation for the natural world.""",
        "type": "Sora 2",
        "quality": 93
    },
    {
        "name": "Sora 2 - 未来科技展示",
        "description": "使用 Sora 2 生成未来科技概念视频",
        "prompt": """Create a futuristic technology showcase video using OpenAI Sora 2, featuring incredible gadgets and innovations. The video begins with a sleek, minimalist laboratory filled with floating holographic displays showing advanced technology concepts. A scientist, wearing a futuristic lab coat and augmented reality glasses, introduces a revolutionary AI assistant that can understand and process emotions in real-time. The video then demonstrates the AI assistant in action, helping a elderly person with a complex task using natural language and empathetic understanding. The scene transitions to a smart home where the AI assistant controls everything from lighting to entertainment, creating a harmonious and personalized living environment. The video then shows the AI assistant in educational settings, helping children learn with personalized, adaptive lessons. The entire video is presented with smooth transitions between scenes, showcasing the practical applications of this advanced AI technology. The video quality should be 4K with 60fps, with stunning visual effects and futuristic design. The style should be similar to Apple product launches, with clean design, smooth animations, and impressive technology demonstrations. The overall mood is exciting and inspiring, evoking a sense of wonder and hope for the future of AI technology.""",
        "type": "Sora 2",
        "quality": 91
    }
]

def create_skill_from_prompt(prompt_data):
    """从 Prompt 数据创建 Skill"""
    name = prompt_data['name']
    description = prompt_data['description']
    prompt = prompt_data['prompt']
    prompt_type = prompt_data['type']
    quality = prompt_data['quality']
    
    # 生成唯一 ID
    content_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
    skill_name = f"{prompt_type.lower()}-{name.lower().replace(' ', '-')}-{content_hash}"
    
    # 创建 skill 目录
    skill_dir = os.path.join(OUTPUT_DIR, skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    
    # 生成 SKILL.md
    skill_md = f"""# {name}

## 描述
{description}

## 类型
- 类型: {prompt_type}
- 质量评分: {quality}/100

## Prompt
```
{prompt[:1000] if len(prompt) > 1000 else prompt}
```

## 特性

### {prompt_type} 相关特性
- 高质量输出
- 专业级提示词
- 详细的场景描述
- 适合专业使用

---

## 使用建议

### 参数调整
- 根据你的模型版本调整提示词
- 使用不同的风格和主题
- 实验不同的参数组合

### 最佳实践
- 从简单的提示词开始
- 逐步增加复杂性
- 记录成功的参数

---

*Skill generated by Clawdbot*
"""

    # 保存 SKILL.md
    with open(os.path.join(skill_dir, 'SKILL.md'), 'w', encoding='utf-8') as f:
        f.write(skill_md)
    
    # 创建 metadata.json
    metadata = {
        "name": name,
        "version": "1.0.0",
        "description": description,
        "author": "Clawdbot",
        "type": prompt_type,
        "quality_score": quality,
        "created_at": datetime.now().isoformat()
    }
    
    with open(os.path.join(skill_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return {
        'name': skill_name,
        'path': skill_dir,
        'md_file': os.path.join(skill_dir, 'SKILL.md'),
        'metadata': metadata,
        'type': prompt_type,
        'quality': quality
    }

def main():
    print("=" * 80)
    print("🎨 生成谷歌生图模型和 Sora 2 的示例 Prompts")
    print("=" * 80)
    print()
    
    # 1. 谷歌生图 Prompts
    print("[1/2] 生成谷歌生图模型 Prompts...")
    google_skills = []
    
    for i, prompt_data in enumerate(GOOGLE_IMAGE_PROMPTS, 1):
        print(f"  [{i}/{len(GOOGLE_IMAGE_PROMPTS)}] {prompt_data['name']}...")
        skill = create_skill_from_prompt(prompt_data)
        google_skills.append(skill)
        print(f"  ✓ 创建成功: {skill['name']}")
    
    print()
    print(f"✅ 谷歌生图 Prompts: {len(google_skills)} 个")
    print()
    
    # 2. Sora 2 Prompts
    print("[2/2] 生成 Sora 2 Prompts...")
    sora2_skills = []
    
    for i, prompt_data in enumerate(SORA2_PROMPTS, 1):
        print(f"  [{i}/{len(SORA2_PROMPTS)}] {prompt_data['name']}...")
        skill = create_skill_from_prompt(prompt_data)
        sora2_skills.append(skill)
        print(f"  ✓ 创建成功: {skill['name']}")
    
    print()
    print(f"✅ Sora 2 Prompts: {len(sora2_skills)} 个")
    print()
    
    # 3. 统计
    all_skills = google_skills + sora2_skills
    
    print("📊 统计信息:")
    print(f"  谷歌生图 Skills: {len(google_skills)}")
    print(f"  Sora 2 Skills: {len(sora2_skills)}")
    print(f"  总计: {len(all_skills)}")
    print()
    
    # 4. 打包
    print("📦 打包成 .skill 文件...")
    
    import zipfile
    packaged_count = 0
    
    for skill in all_skills:
        skill_name = skill['name']
        skill_path = skill['path']
        output_file = os.path.join(PACKAGES_OUTPUT_DIR, f"{skill_name}.skill")
        
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(skill_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, skill_path)
                        zipf.write(file_path, arcname)
            
            packaged_count += 1
            print(f"  ✓ {skill_name}.skill")
        except Exception as e:
            print(f"  ❌ 打包失败 {skill_name}: {e}")
    
    print()
    print(f"✅ 打包完成: {packaged_count} 个")
    print()
    
    # 5. 生成报告
    timestamp = datetime.now().strftime('%Y-%m-%d')
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_skills": len(all_skills),
        "google_image_skills": len(google_skills),
        "sora2_skills": len(sora2_skills),
        "packaged_skills": packaged_count,
        "output_dir": PACKAGES_OUTPUT_DIR
    }
    
    report_file = os.path.join(OUTPUT_DIR, f"google-sora2-skills-report-{timestamp}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 报告已生成: {report_file}")
    print()
    
    # 6. 显示 Top 10
    print("🏆 Top 10 Prompts (按质量排序）:")
    print()
    
    sorted_skills = sorted(all_skills, key=lambda x: x['quality'], reverse=True)
    
    for i, skill in enumerate(sorted_skills[:10], 1):
        print(f"{i}. [{skill['quality']}] {skill['name']} ({skill['type']})")
    
    print()
    print("=" * 80)
    print("✅ 生成完成！")
    print("=" * 80)
    print()
    print(f"📁 输出目录:")
    print(f"  Skills: {OUTPUT_DIR}")
    print(f"  .skill 文件: {PACKAGES_OUTPUT_DIR}")
    print(f"  报告: {report_file}")
    print()
    
    return all_skills, report_file

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
