with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the subhead badge: "MIT ACADEMY OF ENGINEERING // GENAI LAB PRACTICAL ESE // PATHWAY 2"
tagline = """                <div className="mono-meta text-xs text-neutral-500 mb-6">
                  MIT ACADEMY OF ENGINEERING // GENAI LAB PRACTICAL ESE // PATHWAY 2
                </div>"""
content = content.replace(tagline, "")

# 2. Remove the 4-column statistics bar: (13,679, 4 STRATEGIES, GEMINI 2.5, CO1 - CO5)
stats_bar = """              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-16 border-t border-black/10 mono-meta text-xs text-neutral-500">
                <div>
                  <span className="block text-black font-bold text-lg mb-1">13,679</span>
                  SciQ Science Items
                </div>
                <div>
                  <span className="block text-black font-bold text-lg mb-1">4 STRATEGIES</span>
                  Controlled Experiments
                </div>
                <div>
                  <span className="block text-black font-bold text-lg mb-1">GEMINI 2.5</span>
                  Flash & Flash-Lite
                </div>
                <div>
                  <span className="block text-black font-bold text-lg mb-1">CO1 — CO5</span>
                  ESE Syllabus Aligned
                </div>
              </div>"""
content = content.replace(stats_bar, "")

# 3. Clean up any remaining footer branding referring to MIT AOE
content = content.replace("""          <div className="mono-meta text-xs text-neutral-400">
            MIT ACADEMY OF ENGINEERING // GENAI LAB ESE
          </div>""", """          <div className="mono-meta text-xs text-neutral-400">
            GENIQ INTELLIGENCE PLATFORM
          </div>""")

with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Home page elements removed cleanly!")
