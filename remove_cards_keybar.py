with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the 3 cards section (Architecture Highlights: Multimodal Document Ingestion, Psychometric Prompting, Automated Evaluation)
cards_section_start = "{/* Architecture Highlights */}"
cards_section_end = "</section>"

if cards_section_start in content:
    idx_start = content.find(cards_section_start)
    idx_end = content.find(cards_section_end, idx_start) + len(cards_section_end)
    content = content[:idx_start] + content[idx_end:]

# 2. Hide the API key configuration box on the Generate page once the key is already configured
# (Only show it if health is not configured, or remove the big banner completely)
old_key_bar_start = "{/* API Warning & Key Configuration Bar */}"
new_key_bar = """            {/* API Key Configuration (Only shown if key is missing) */}
            {health && !health.api_configured && (
              <div className="mb-8 p-5 border border-amber-300 bg-amber-50 rounded-sm">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <span className="font-bold text-sm text-amber-900 block">Gemini API Key Required</span>
                    <p className="text-xs text-amber-800">
                      Paste your Google Gemini API key to activate live question synthesis.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="password"
                      value={apiKeyInput}
                      onChange={(e) => setApiKeyInput(e.target.value)}
                      placeholder="Enter GEMINI_API_KEY..."
                      className="p-2 border border-black/20 text-xs w-64 outline-none font-mono bg-white focus:border-black"
                    />
                    <button
                      onClick={async () => {
                        if (!apiKeyInput.trim()) return;
                        setKeySaving(true);
                        setKeyMsg(null);
                        try {
                          await api.setApiKey(apiKeyInput.trim());
                          const h = await api.getHealth();
                          setHealth(h);
                          setKeyMsg('API key saved!');
                          setApiKeyInput('');
                        } catch (e: any) {
                          setKeyMsg(`Error: ${e.message}`);
                        } finally {
                          setKeySaving(false);
                        }
                      }}
                      disabled={keySaving}
                      className="px-4 py-2 bg-black text-white text-xs font-mono uppercase tracking-wider hover:bg-neutral-800 disabled:opacity-50"
                    >
                      {keySaving ? 'Saving...' : 'Save Key'}
                    </button>
                  </div>
                </div>
                {keyMsg && (
                  <p className="text-xs font-mono text-green-700 mt-2">{keyMsg}</p>
                )}
              </div>
            )}"""

if old_key_bar_start in content:
    idx1 = content.find(old_key_bar_start)
    # find closing tag of the box
    idx2 = content.find("</div>\n            </div>", idx1) + len("</div>\n            </div>")
    content = content[:idx1] + new_key_bar + content[idx2:]

with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed 3 cards and hid API key box when already configured!")
