with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove unused 'Play' icon
content = content.replace("import { ArrowUpRight, BookOpen, Play, Upload, RefreshCw, Trash2, Award } from 'lucide-react';", "import { ArrowUpRight, BookOpen, Upload, RefreshCw, Trash2, Award } from 'lucide-react';")

# Remove unused states and functions related to running experiments
content = content.replace("  // Research experiments state\n  const [experimentsData, setExperimentsData] = useState<Record<string, any>>({});\n  const [runningExpId, setRunningExpId] = useState<string | null>(null);", "")

func_to_remove = """  const handleRunExperiment = async (expId: string) => {
    setRunningExpId(expId);
    try {
      await api.runExperiment(expId, 5);
      loadExperiments();
    } catch (e: any) {
      alert(`Experiment error: ${e.message}`);
    } finally {
      setRunningExpId(null);
    }
  };"""

content = content.replace(func_to_remove, "")
content = content.replace("  const loadExperiments = () => {\n    api.getExperiments().then(setExperimentsData).catch(console.error);\n  };\n", "")
content = content.replace(" else if (currentPage === 'analytics') {\n      loadExperiments();\n    }", "")

with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Cleaned up unused research states!")
