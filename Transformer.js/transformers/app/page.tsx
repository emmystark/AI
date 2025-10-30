'use client'

import { useState, useEffect, useRef } from 'react';

// Partial list of languages (expand as needed)
const LANGUAGES = {
  "English": "eng_Latn",
  "French": "fra_Latn",
  "Spanish": "spa_Latn",
  "German": "deu_Latn",
  "Chinese (Simplified)": "zho_Hans",
  "Arabic": "arb_Arab",
  "Japanese": "jpn_Jpan",
  // Add more: full list at https://github.com/facebookresearch/flores/blob/main/flores200/README.md
};

export default function Home() {
  const [input, setInput] = useState('Hello, how are you?');
  const [output, setOutput] = useState('');
  const [sourceLang, setSourceLang] = useState('eng_Latn');
  const [targetLang, setTargetLang] = useState('fra_Latn');
  const [ready, setReady] = useState(null);
  const [disabled, setDisabled] = useState(false);
  const [progressItems, setProgressItems] = useState([]);

  const worker = useRef<Worker | null>(null);

  useEffect(() => {
    if (!worker.current) {
      worker.current = new Worker(new URL('./worker.js', import.meta.url), {
        type: 'module',
      });
    }

    const onMessageReceived = (e: MessageEvent) => {
      switch (e.data.status) {
        case 'initiate':
          setReady(false);
          setProgressItems(prev => [...prev, e.data]);
          break;
        case 'progress':
          setProgressItems(prev =>
            prev.map(item =>
              item.file === e.data.file ? { ...item, progress: e.data.progress } : item
            )
          );
          break;
        case 'done':
          setProgressItems(prev => prev.filter(item => item.file !== e.data.file));
          break;
        case 'ready':
          setReady(true);
          break;
        case 'complete':
          setOutput(e.data.output[0].translation_text);
          setDisabled(false);
          break;
      }
    };

    worker.current.addEventListener('message', onMessageReceived);

    return () => worker.current?.removeEventListener('message', onMessageReceived);
  }, []);

  const translate = () => {
    setDisabled(true);
    setOutput('');
    if (worker.current) {
      worker.current.postMessage({
        text: input,
        src_lang: sourceLang,
        tgt_lang: targetLang,
      });
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-12">
      <h1 className="text-5xl font-bold mb-2 text-center">Transformers.js Translation Demo</h1>
      <h2 className="text-2xl mb-4 text-center">Multilingual Translation in Next.js</h2>

      <div className="w-full max-w-md">
        <label>Source Language:</label>
        <select value={sourceLang} onChange={(e) => setSourceLang(e.target.value)} className="w-full p-2 mb-4 border">
          {Object.entries(LANGUAGES).map(([name, code]) => (
            <option key={code} value={code}>{name}</option>
          ))}
        </select>

        <label>Target Language:</label>
        <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)} className="w-full p-2 mb-4 border">
          {Object.entries(LANGUAGES).map(([name, code]) => (
            <option key={code} value={code}>{name}</option>
          ))}
        </select>

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter text to translate"
          className="w-full p-2 border mb-4"
          rows={4}
        />

        <button onClick={translate} disabled={disabled} className="w-full p-2 bg-blue-500 text-white mb-4">
          {disabled ? 'Translating...' : 'Translate'}
        </button>

        <textarea
          value={output}
          readOnly
          placeholder="Translation will appear here"
          className="w-full p-2 border"
          rows={4}
        />

        {ready === false && (
          <div className="mt-4">
            <p>Loading model... (only once, ~2.4GB)</p>
            {progressItems.map((item) => (
              <div key={item.file} className="mt-2">
                <p>{item.file}: {item.progress}%</p>
                <div className="w-full bg-gray-200">
                  <div className="bg-blue-500 h-2" style={{ width: `${item.progress}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}