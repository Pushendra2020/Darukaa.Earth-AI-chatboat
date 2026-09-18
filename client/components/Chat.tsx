"use client";

import { useState } from "react";
import { sendMessage, ChatResponse } from "../lib/api";

export default function Chat() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [environment, setEnvironment] = useState({
    rainfall: 800,
    soil_organic_carbon: 0.4,
    land_use: "cropland"
  });

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await sendMessage(
        userMessage.content,
        conversationId,
        environment
      );

      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      setMessages(prev => [...prev, { role: "assistant", response }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: "assistant", error: "An error occurred while contacting the analysis engine." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-[30px] border border-emerald-200/70 bg-white/75 shadow-[0_30px_80px_rgba(15,118,110,0.12)] backdrop-blur-xl">
      <div className="border-b border-emerald-100 bg-gradient-to-r from-emerald-50 via-white to-teal-50 px-4 py-4 md:px-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-emerald-700/80">
              Environment context
            </p>
            <h2 className="mt-1 text-lg font-bold text-slate-800">Field parameters</h2>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <label className="rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
              <span className="mb-1 block text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Rainfall
              </span>
              <input
                type="number"
                value={environment.rainfall}
                onChange={e => setEnvironment({ ...environment, rainfall: Number(e.target.value) })}
                className="w-full bg-transparent text-sm font-medium text-slate-800 outline-none"
              />
            </label>

            <label className="rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
              <span className="mb-1 block text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Soil SOC
              </span>
              <input
                type="number"
                step="0.1"
                value={environment.soil_organic_carbon}
                onChange={e => setEnvironment({ ...environment, soil_organic_carbon: Number(e.target.value) })}
                className="w-full bg-transparent text-sm font-medium text-slate-800 outline-none"
              />
            </label>

            <label className="rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
              <span className="mb-1 block text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Land use
              </span>
              <input
                type="text"
                value={environment.land_use}
                onChange={e => setEnvironment({ ...environment, land_use: e.target.value })}
                className="w-full bg-transparent text-sm font-medium text-slate-800 outline-none"
              />
            </label>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto bg-[linear-gradient(180deg,rgba(240,253,250,0.6),rgba(255,255,255,0.75))] p-4 md:p-5">
        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          {messages.length === 0 && (
            <div className="mt-10 rounded-[24px] border border-dashed border-emerald-200 bg-white/70 p-6 text-center text-slate-600 shadow-sm">
              <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 text-xl text-emerald-700">
                🌿
              </div>
              <h3 className="text-xl font-semibold text-slate-900">Ask about biodiversity, resilience, or land performance</h3>
              <p className="mt-2 text-sm text-slate-500">
                Get evidence-based recommendations based on ecosystem context and field conditions.
              </p>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[90%] rounded-[22px] px-4 py-3 shadow-sm md:max-w-[82%] ${
                  m.role === "user"
                    ? "bg-gradient-to-br from-emerald-600 to-teal-700 text-white"
                    : "border border-slate-200 bg-white text-slate-800"
                }`}
              >
                {m.role === "user" ? (
                  m.content
                ) : (
                  <AssistantMessage response={m.response} error={m.error} />
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 rounded-[20px] border border-slate-200 bg-white px-4 py-3 shadow-sm text-slate-500">
                <div className="h-2.5 w-2.5 animate-bounce rounded-full bg-emerald-500 [animation-delay:-0.2s]" />
                <div className="h-2.5 w-2.5 animate-bounce rounded-full bg-emerald-500 [animation-delay:-0.1s]" />
                <div className="h-2.5 w-2.5 animate-bounce rounded-full bg-emerald-500" />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="border-t border-emerald-100 bg-white/80 p-4 md:p-5">
        <div className="mx-auto flex max-w-4xl gap-3">
          <input
            type="text"
            className="flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100"
            placeholder="Ask about the ecosystem, soil, rainfall, or land management..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSend()}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-700 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-600/20 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

function AssistantMessage({ response, error }: { response?: ChatResponse; error?: string }) {
  if (error) return <div className="text-sm font-medium text-red-500">{error}</div>;
  if (!response) return null;

  return (
    <div className="flex flex-col gap-4">
      <div className="leading-relaxed text-slate-700">{response.answer}</div>

      {response.recommendations && response.recommendations.length > 0 && (
        <div className="flex flex-col gap-3 pt-2">
          <h4 className="border-b border-slate-200 pb-1 text-sm font-bold uppercase tracking-[0.18em] text-slate-500">
            Recommendations
          </h4>
          {response.recommendations.map((rec, i) => (
            <div key={i} className="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700 shadow-sm">
              <div className="font-semibold text-emerald-700">{rec.action}</div>
              <div className="mt-2 text-slate-600">
                <span className="font-semibold text-slate-700">Why:</span> {rec.why_it_works}
              </div>

              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                <div>
                  <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Metrics
                  </span>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {rec.impacted_metrics.map(m => (
                      <span key={m} className="rounded-full bg-emerald-100 px-2 py-1 text-[11px] font-medium text-emerald-800">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Horizon
                  </span>
                  <div className="mt-2 text-sm font-medium text-slate-700">{rec.time_horizon}</div>
                </div>
              </div>

              {rec.evidence && rec.evidence.length > 0 && (
                <div className="mt-3 border-t border-slate-200 pt-3">
                  <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Evidence
                  </span>
                  <div className="mt-2 flex flex-col gap-2">
                    {rec.evidence.map((ev, j) => (
                      <div key={j} className="rounded-xl bg-white p-2 text-xs text-slate-600">
                        <div className="font-semibold text-slate-700">"{ev.title}" ({ev.year})</div>
                        {ev.page && <div className="mt-1 text-slate-400">Page: {ev.page}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
