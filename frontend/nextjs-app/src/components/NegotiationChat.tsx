"use client";

import React, { useState, useRef, useEffect } from "react";
import { COLORS, Icon, Card } from "./ui";
import { chatNegotiation } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  feedback?: string;
  sentiment?: string;
}

export const NegotiationChat = ({ 
  jobTitle = "Software Engineer", 
  targetSalaryLpa = 25 
}: { 
  jobTitle?: string; 
  targetSalaryLpa?: number;
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "ai",
      content: `Hi! Thanks for taking the time to chat. We're thrilled to extend an offer for the ${jobTitle} position. We'd like to offer you a starting salary of ${Math.round(targetSalaryLpa * 0.8)} LPA. How does that sound?`
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { id: Date.now().toString(), role: "user", content: input };
    const newHistory = [...messages, userMsg];
    
    setMessages(newHistory);
    setInput("");
    setLoading(true);

    try {
      const historyPayload = messages.map(m => ({ role: m.role, content: m.content }));
      const response = await chatNegotiation(jobTitle, targetSalaryLpa, historyPayload, userMsg.content);
      
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: response.aiResponse,
        feedback: response.feedback,
        sentiment: response.sentiment,
      };
      setMessages([...newHistory, aiMsg]);
    } catch (error) {
      console.error("Negotiation error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card style={{ display: "flex", flexDirection: "column", height: 600, padding: 0, overflow: "hidden" }}>
      <div style={{ padding: "16px 20px", borderBottom: `1px solid ${COLORS.borderLight}`, background: COLORS.bg, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: 16, margin: 0, color: COLORS.text }}>Salary Negotiation Practice</h2>
          <p style={{ fontSize: 13, margin: "2px 0 0", color: COLORS.textMuted }}>Target: {targetSalaryLpa} LPA</p>
        </div>
        <div style={{ padding: "4px 10px", borderRadius: 4, background: COLORS.brandLight, color: COLORS.brand, fontSize: 12, fontWeight: 500 }}>
          AI HR Recruiter
        </div>
      </div>
      
      <div style={{ flex: 1, overflowY: "auto", padding: "20px", display: "flex", flexDirection: "column", gap: 16, background: "#fafafa" }}>
        {messages.map((msg) => (
          <div key={msg.id} style={{ display: "flex", flexDirection: "column", alignItems: msg.role === "user" ? "flex-end" : "flex-start" }}>
            <div style={{ 
              maxWidth: "80%", 
              padding: "12px 16px", 
              borderRadius: 12, 
              background: msg.role === "user" ? COLORS.brand : COLORS.card,
              color: msg.role === "user" ? "#fff" : COLORS.text,
              border: msg.role === "ai" ? `1px solid ${COLORS.borderLight}` : "none",
              fontSize: 14,
              lineHeight: 1.5
            }}>
              {msg.content}
            </div>
            {msg.role === "ai" && msg.feedback && (
              <div style={{ 
                marginTop: 6, 
                maxWidth: "75%", 
                padding: "8px 12px", 
                borderRadius: 8, 
                background: COLORS.warningBg,
                border: "1px solid #FDE68A",
                color: COLORS.warning,
                fontSize: 12,
                display: "flex",
                alignItems: "flex-start",
                gap: 6
              }}>
                <Icon name="zap" size={14} style={{ flexShrink: 0, marginTop: 2 }} />
                <span><strong>Feedback:</strong> {msg.feedback}</span>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ display: "flex", gap: 4, padding: "12px 16px", background: COLORS.card, borderRadius: 12, width: "fit-content", border: `1px solid ${COLORS.borderLight}` }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: COLORS.textLight, animation: "bounce 1.4s infinite ease-in-out both" }}></div>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: COLORS.textLight, animation: "bounce 1.4s infinite ease-in-out both", animationDelay: "0.2s" }}></div>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: COLORS.textLight, animation: "bounce 1.4s infinite ease-in-out both", animationDelay: "0.4s" }}></div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div style={{ padding: "16px 20px", borderTop: `1px solid ${COLORS.borderLight}`, background: COLORS.card, display: "flex", gap: 10 }}>
        <input 
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your response..."
          style={{ flex: 1, padding: "10px 14px", borderRadius: 8, border: `1px solid ${COLORS.border}`, outline: "none", fontSize: 14 }}
        />
        <button 
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{ 
            padding: "0 20px", 
            borderRadius: 8, 
            background: loading || !input.trim() ? COLORS.border : COLORS.brand,
            color: "#fff",
            border: "none",
            cursor: loading || !input.trim() ? "default" : "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}
        >
          <Icon name="send" size={16} color="#fff" />
        </button>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }
      `}</style>
    </Card>
  );
};
