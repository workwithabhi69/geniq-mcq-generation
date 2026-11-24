with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CurrentPage state type definition
content = content.replace(
    "const [currentPage, setCurrentPage] = useState<'home' | 'generate' | 'research' | 'analytics' | 'bank' | 'quiz' | 'docs'>('home');",
    "const [currentPage, setCurrentPage] = useState<'home' | 'generate' | 'analytics' | 'bank' | 'quiz'>('home');"
)

# 2. Remove Research Lab button from navigation
research_btn = """          <button 
            onClick={() => setCurrentPage('research')} 
            className={`transition-colors hover:text-black ${currentPage === 'research' ? 'text-black font-semibold' : 'text-neutral-500'}`}
          >
            Research Lab
          </button>"""

docs_btn = """          <button 
            onClick={() => setCurrentPage('docs')} 
            className={`transition-colors hover:text-black ${currentPage === 'docs' ? 'text-black font-semibold' : 'text-neutral-500'}`}
          >
            Docs
          </button>"""

content = content.replace(research_btn, "")
content = content.replace(docs_btn, "")

# 3. Remove Explore Research Lab CTA from Landing hero
hero_research_cta = """                  <button 
                    onClick={() => setCurrentPage('research')}
                    className="px-8 py-4 border border-black/20 text-black text-sm font-semibold hover:border-black transition-all"
                  >
                    Explore Research Lab
                  </button>"""
content = content.replace(hero_research_cta, "")

# 4. Remove useEffect trigger for research
content = content.replace(
    "if (currentPage === 'bank' || currentPage === 'quiz') {\n      loadQuestions();\n    } else if (currentPage === 'research' || currentPage === 'analytics') {\n      loadExperiments();\n    }",
    "if (currentPage === 'bank' || currentPage === 'quiz') {\n      loadQuestions();\n    } else if (currentPage === 'analytics') {\n      loadExperiments();\n    }"
)

# 5. Remove Page 3 (Research Lab) block
research_page_start = "{/* ================= PAGE 3: RESEARCH LABORATORY ================= */}"
analytics_page_start = "{/* ================= PAGE 4: ANALYTICS ================= */}"

if research_page_start in content and analytics_page_start in content:
    idx1 = content.find(research_page_start)
    idx2 = content.find(analytics_page_start)
    content = content[:idx1] + content[idx2:]

# 6. Remove Page 7 (Docs) block
docs_page_start = "{/* ================= PAGE 7: DOCUMENTATION ================= */}"
main_end = "</main>"

if docs_page_start in content and main_end in content:
    idx3 = content.find(docs_page_start)
    idx4 = content.find(main_end, idx3)
    content = content[:idx3] + content[idx4:]

with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Research Lab and Docs successfully removed from App.tsx!")
