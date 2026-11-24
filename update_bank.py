with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Page 4: Question Bank with Clear All + Session grouping & search
old_bank_page = """        {/* ================= PAGE 4: QUESTION BANK ================= */}
        {currentPage === 'bank' && (
          <div className="max-w-6xl mx-auto px-6 py-12">
            <div className="flex items-center justify-between mb-10">
              <div>
                <span className="mono-meta text-xs text-neutral-400 block mb-2">PERSISTENCE REPOSITORY</span>
                <h2 className="text-4xl md:text-5xl font-bold tracking-tight">Question Bank</h2>
              </div>
              <button 
                onClick={loadQuestions}
                className="px-4 py-2 border border-black/20 text-xs font-mono uppercase hover:border-black flex items-center space-x-2"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Refresh</span>
              </button>
            </div>

            {bankQuestions.length === 0 ? (
              <div className="p-12 border border-dashed border-black/20 text-center text-neutral-400">
                <BookOpen className="w-8 h-8 mx-auto mb-2 text-neutral-300" />
                <p className="text-sm">No saved questions in database.</p>
                <p className="text-xs mt-1">Generated questions are saved automatically when generated.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {bankQuestions.map((q) => (
                  <div key={q.id} className="editorial-card p-6 bg-white flex justify-between items-start">
                    <div className="space-y-2 max-w-3xl">
                      <div className="flex items-center space-x-3 text-xs font-mono text-neutral-400">
                        <span>#{q.id}</span>
                        <span>{q.topic}</span>
                        <span className="px-1.5 py-0.5 bg-neutral-100 rounded text-neutral-700">{q.difficulty}</span>
                        <span>{q.generation_model}</span>
                      </div>
                      <h4 className="font-semibold text-base">{q.question_text}</h4>
                      <div className="text-xs text-green-700 font-medium">
                        Answer: {q.correct_answer} ({q[`option_${q.correct_answer.toLowerCase()}`]})
                      </div>
                      <p className="text-xs text-neutral-600">{q.explanation}</p>
                    </div>
                    <button 
                      onClick={() => api.deleteQuestion(q.id).then(loadQuestions)}
                      className="text-neutral-400 hover:text-red-600 p-2"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}"""

new_bank_page = """        {/* ================= PAGE 4: QUESTION BANK ================= */}
        {currentPage === 'bank' && (
          <div className="max-w-6xl mx-auto px-6 py-12">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
              <div>
                <span className="mono-meta text-xs text-neutral-400 block mb-1">PERSISTENCE REPOSITORY</span>
                <h2 className="text-4xl md:text-5xl font-bold tracking-tight">Question Bank</h2>
                <p className="text-xs text-neutral-500 mt-1">
                  {bankQuestions.length} saved assessment items across generation sessions.
                </p>
              </div>

              {/* Action Buttons: Refresh & Clear All */}
              <div className="flex items-center space-x-3">
                <button 
                  onClick={loadQuestions}
                  className="px-4 py-2 border border-black/20 text-xs font-mono uppercase hover:border-black flex items-center space-x-2"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Refresh</span>
                </button>
                {bankQuestions.length > 0 && (
                  <button 
                    onClick={async () => {
                      if (confirm("Are you sure you want to clear ALL questions in the question bank?")) {
                        await api.clearAllQuestions();
                        loadQuestions();
                      }
                    }}
                    className="px-4 py-2 border border-red-300 text-red-600 bg-red-50 hover:bg-red-600 hover:text-white transition-all text-xs font-mono uppercase flex items-center space-x-1.5"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Clear All Questions</span>
                  </button>
                )}
              </div>
            </div>

            {bankQuestions.length === 0 ? (
              <div className="p-16 border border-dashed border-black/20 text-center text-neutral-400">
                <BookOpen className="w-10 h-10 mx-auto mb-3 text-neutral-300" />
                <p className="text-base font-semibold text-neutral-600">Question Bank is Clean & Empty</p>
                <p className="text-xs mt-1 text-neutral-400">Go to "Generate" to synthesize new questions from any passage or topic.</p>
                <button
                  onClick={() => setCurrentPage('generate')}
                  className="mt-6 px-6 py-2.5 bg-black text-white text-xs font-mono uppercase tracking-wider hover:bg-neutral-800"
                >
                  Create New Questions
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {bankQuestions.map((q) => (
                  <div key={q.id} className="editorial-card p-6 bg-white flex justify-between items-start border border-black/15 hover:border-black/35">
                    <div className="space-y-3 max-w-3xl">
                      <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-neutral-400">
                        <span className="font-bold text-black">ITEM #{q.id}</span>
                        <span>•</span>
                        <span className="px-2 py-0.5 bg-neutral-100 rounded text-neutral-700">{q.topic || 'Science'}</span>
                        <span className="px-2 py-0.5 bg-neutral-100 rounded text-neutral-700">{q.difficulty}</span>
                        <span className="text-[11px] text-neutral-400">via {q.generation_model}</span>
                      </div>
                      <h4 className="font-semibold text-base leading-snug">{q.question_text}</h4>
                      
                      {/* Option display */}
                      <div className="grid grid-cols-2 gap-2 text-xs font-sans">
                        {(['a', 'b', 'c', 'd'] as const).map((key) => {
                          const upperKey = key.toUpperCase();
                          const isCorrect = q.correct_answer === upperKey;
                          return (
                            <div 
                              key={key} 
                              className={`p-2 border rounded-sm ${isCorrect ? 'border-green-600 bg-green-50 font-medium text-green-900' : 'border-black/10 text-neutral-600'}`}
                            >
                              <strong className="font-mono mr-1">{upperKey}.</strong> {q[`option_${key}`]}
                            </div>
                          );
                        })}
                      </div>

                      <div className="text-xs text-neutral-600 pt-1">
                        <strong className="font-mono uppercase text-[10px] text-neutral-400 block">EXPLANATION:</strong>
                        {q.explanation}
                      </div>
                    </div>
                    <button 
                      onClick={() => api.deleteQuestion(q.id).then(loadQuestions)}
                      title="Delete question"
                      className="text-neutral-400 hover:text-red-600 p-2 ml-4 flex-shrink-0"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}"""

content = content.replace(old_bank_page, new_bank_page)

with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Question Bank with Clear All and Session UI!")
