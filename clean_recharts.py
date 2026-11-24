with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix unused imports
content = content.replace(
    "import { ArrowUpRight, BookOpen, Upload, RefreshCw, Trash2, Award, CheckCircle, XCircle, ArrowRight, ArrowLeft, BarChart2, Zap, Target, PieChart as PieIcon, Cpu } from 'lucide-react';",
    "import { ArrowUpRight, BookOpen, Upload, RefreshCw, Trash2, Award, CheckCircle, XCircle, ArrowRight, ArrowLeft, BarChart2, Target, Cpu } from 'lucide-react';"
)

content = content.replace(
    "import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, PieChart, Pie, Cell } from 'recharts';",
    "import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';"
)

# Remove unused difficultyDist
unused_dist = """          // Topic & Difficulty Distribution
          const difficultyDist = [
            { name: 'Easy', value: 35, color: '#000000' },
            { name: 'Medium', value: 45, color: '#525252' },
            { name: 'Hard', value: 20, color: '#A3A3A3' },
          ];"""
content = content.replace(unused_dist, "")

with open(r'C:\Users\ag634\.gemini\antigravity\scratch\geniq\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Cleaned up unused Recharts imports!")
