with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update State
old_state = """  const [numQuestions] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);"""

new_state = """  const [numQuestions, setNumQuestions] = useState(3);
  const [showAnswers, setShowAnswers] = useState(false);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [isGenerating, setIsGenerating] = useState(false);"""

content = content.replace(old_state, new_state)

# 2. Add question count selector
old_form = """                {/* Configuration Parameters */}
                <div className="grid grid-cols-2 gap-4">"""

new_form = """                {/* Configuration Parameters */}
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-mono uppercase text-neutral-500 mb-2">Count</label>
                    <select 
                      value={numQuestions}
                      onChange={(e) => setNumQuestions(Number(e.target.value))}
                      className="w-full p-2.5 border border-black/20 text-sm outline-none bg-white font-mono"
                    >
                      <option value={1}>1 Question</option>
                      <option value={3}>3 Questions</option>
                      <option value={5}>5 Questions</option>
                      <option value={10}>10 Questions</option>
                    </select>
                  </div>"""

content = content.replace(old_form, new_form)

# 3. Add toggle button for answer keys in header
old_header = """                <div className="flex items-center justify-between pb-3 border-b border-black/10 mb-6">
                  <span className="mono-meta text-xs text-neutral-500">GENERATED OUTPUTS</span>
                  <span className="text-xs text-neutral-400">{generatedList.length} items synthesized</span>
                </div>"""

new_header = """                <div className="flex items-center justify-between pb-3 border-b border-black/10 mb-6">
                  <div>
                    <span className="mono-meta text-xs text-neutral-500 block">GENERATED OUTPUTS</span>
                    <span className="text-xs text-neutral-400">{generatedList.length} items synthesized</span>
                  </div>
                  {generatedList.length > 0 && (
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setShowAnswers(!showAnswers)}
                        className="px-3 py-1.5 border border-black/30 text-xs font-mono uppercase hover:bg-black hover:text-white transition-all"
                      >
                        {showAnswers ? "Hide Solutions" : "Reveal Solutions"}
                      </button>
                    </div>
                  )}
                </div>"""

content = content.replace(old_header, new_header)

# 4. Interactive option selection: do not reveal green border by default unless answered or showAnswers is True
old_options = """                        {/* Options A, B, C, D */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                          {(['A', 'B', 'C', 'D'] as const).map((key) => {
                            const isCorrect = mcq.correct_answer === key;
                            return (
                              <div 
                                key={key}
                                className={`p-3 border rounded-sm ${isCorrect ? 'border-green-600 bg-green-50/50' : 'border-black/10'}`}
                              >
                                <span className="font-bold mr-2 text-xs font-mono">{key}.</span>
                                <span>{mcq.options[key]}</span>
                              </div>
                            );
                          })}
                        </div>"""

new_options = """                        {/* Options A, B, C, D */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                          {(['A', 'B', 'C', 'D'] as const).map((key) => {
                            const userSelected = userAnswers[idx] === key;
                            const isCorrect = mcq.correct_answer === key;
                            let cardStyle = 'border-black/15 hover:border-black/40';

                            if (showAnswers) {
                              if (isCorrect) cardStyle = 'border-green-600 bg-green-50/70 font-semibold';
                              else if (userSelected && !isCorrect) cardStyle = 'border-red-500 bg-red-50/50 line-through';
                            } else if (userSelected) {
                              cardStyle = 'border-black bg-neutral-100 font-semibold';
                            }

                            return (
                              <div 
                                key={key}
                                onClick={() => setUserAnswers({ ...userAnswers, [idx]: key })}
                                className={`p-3.5 border rounded-sm cursor-pointer transition-all ${cardStyle}`}
                              >
                                <span className="font-bold mr-2 text-xs font-mono">{key}.</span>
                                <span>{mcq.options[key]}</span>
                              </div>
                            );
                          })}
                        </div>"""

content = content.replace(old_options, new_options)

# 5. Hide explanation and source evidence unless showAnswers is toggled or user attempted
old_explanation = """                        {/* Explanation & Evidence */}
                        <div className="pt-3 border-t border-black/10 space-y-2 text-xs">
                          <div>
                            <span className="font-mono text-neutral-400 uppercase">Correct Answer: </span>
                            <span className="font-bold text-green-700">{mcq.correct_answer} ({mcq.options[mcq.correct_answer as keyof typeof mcq.options]})</span>
                          </div>
                          <div>
                            <span className="font-mono text-neutral-400 uppercase">Explanation: </span>
                            <span className="text-neutral-700">{mcq.explanation}</span>
                          </div>
                          <div className="p-2 bg-neutral-50 text-neutral-600 font-mono text-[11px] border border-black/5">
                            <span className="text-neutral-400 block mb-1">SOURCE EVIDENCE:</span>
                            "{mcq.source_evidence}"
                          </div>
                        </div>"""

new_explanation = """                        {/* Explanation & Evidence (Only shown when toggled or student requests) */}
                        {showAnswers ? (
                          <div className="pt-3 border-t border-black/10 space-y-2 text-xs animate-in fade-in">
                            <div>
                              <span className="font-mono text-neutral-400 uppercase">Correct Answer: </span>
                              <span className="font-bold text-green-700">{mcq.correct_answer} ({mcq.options[mcq.correct_answer as keyof typeof mcq.options]})</span>
                            </div>
                            <div>
                              <span className="font-mono text-neutral-400 uppercase">Explanation: </span>
                              <span className="text-neutral-700">{mcq.explanation}</span>
                            </div>
                            <div className="p-2 bg-neutral-50 text-neutral-600 font-mono text-[11px] border border-black/5">
                              <span className="text-neutral-400 block mb-1">SOURCE EVIDENCE:</span>
                              "{mcq.source_evidence}"
                            </div>
                          </div>
                        ) : (
                          <div className="pt-2 text-right">
                            <button
                              onClick={() => setShowAnswers(true)}
                              className="text-[11px] font-mono text-neutral-500 hover:text-black underline uppercase"
                            >
                              Check Answer & Explanation
                            </button>
                          </div>
                        )}"""

content = content.replace(old_explanation, new_explanation)

with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated App.tsx successfully!')
