"use client";

import React from "react";
import { COLORS, Icon } from "./ui";

export type NavPage =
  | "dashboard"
  | "jobs"
  | "resume"
  | "kanban"
  | "interview"
  | "demo"
  | "about";

const MAIN_NAV: { id: NavPage; label: string; icon: string }[] = [
  { id: "dashboard", label: "Dashboard", icon: "grid" },
  { id: "jobs", label: "Jobs Feed", icon: "briefcase" },
  { id: "resume", label: "Resume & ATS", icon: "file-text" },
  { id: "kanban", label: "Kanban Board", icon: "layout" },
  { id: "interview", label: "Mock Interview", icon: "mic" },
];

const SECONDARY_NAV: { id: NavPage; label: string; icon: string }[] = [
  { id: "demo", label: "See a Demo", icon: "play" },
  { id: "about", label: "About", icon: "info" },
];

export const Sidebar = ({
  active,
  setActive,
  collapsed,
  onToggle,
}: {
  active: NavPage;
  setActive: (id: NavPage) => void;
  collapsed: boolean;
  onToggle: () => void;
}) => {
  const w = collapsed ? 60 : 220;

  const NavBtn = ({
    id,
    label,
    icon,
  }: {
    id: NavPage;
    label: string;
    icon: string;
  }) => {
    const isActive = active === id;
    return (
      <button
        onClick={() => setActive(id)}
        title={collapsed ? label : undefined}
        style={{
          display: "flex",
          alignItems: "center",
          gap: collapsed ? 0 : 10,
          justifyContent: collapsed ? "center" : "flex-start",
          width: "100%",
          padding: collapsed ? "9px 0" : "8px 10px",
          borderRadius: 6,
          border: "none",
          cursor: "pointer",
          background: isActive ? COLORS.sidebarActive : "transparent",
          color: isActive ? COLORS.brand : COLORS.textMuted,
          fontSize: 13.5,
          fontWeight: isActive ? 500 : 400,
          marginBottom: 2,
          textAlign: "left",
          transition: "background 0.12s, color 0.12s",
          whiteSpace: "nowrap",
          overflow: "hidden",
        }}
      >
        <Icon
          name={icon}
          size={15}
          color={isActive ? COLORS.brand : COLORS.textMuted}
          style={{ flexShrink: 0 }}
        />
        {!collapsed && label}
      </button>
    );
  };

  return (
    <div
      style={{
        width: w,
        minWidth: w,
        height: "100vh",
        background: COLORS.sidebar,
        borderRight: `1px solid ${COLORS.border}`,
        display: "flex",
        flexDirection: "column",
        position: "sticky",
        top: 0,
        transition: "width 0.2s ease, min-width 0.2s ease",
        overflow: "hidden",
      }}
    >
      {/* Logo + collapse toggle */}
      <div
        style={{
          padding: collapsed ? "14px 0" : "16px 16px 14px",
          borderBottom: `1px solid ${COLORS.borderLight}`,
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed ? "center" : "space-between",
          gap: 10,
        }}
      >
        {!collapsed && (
          <div style={{ display: "flex", alignItems: "center", gap: 10, minWidth: 0 }}>
            <div
              style={{
                width: 30,
                height: 30,
                borderRadius: 7,
                background: COLORS.brand,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <Icon name="cpu" size={14} color="#fff" />
            </div>
            <div style={{ minWidth: 0 }}>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: COLORS.text,
                  letterSpacing: "-0.2px",
                  whiteSpace: "nowrap",
                }}
              >
                Job Search AI
              </div>
              <div style={{ fontSize: 11, color: COLORS.textLight, fontWeight: 400 }}>
                Pro Workspace
              </div>
            </div>
          </div>
        )}

        {collapsed && (
          <div
            style={{
              width: 30,
              height: 30,
              borderRadius: 7,
              background: COLORS.brand,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Icon name="cpu" size={14} color="#fff" />
          </div>
        )}

        <button
          onClick={onToggle}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          style={{
            width: 26,
            height: 26,
            borderRadius: 5,
            border: `1px solid ${COLORS.border}`,
            background: COLORS.card,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            flexShrink: 0,
            padding: 0,
          }}
        >
          <Icon
            name={collapsed ? "chevron-right" : "chevron-left"}
            size={13}
            color={COLORS.textMuted}
          />
        </button>
      </div>

      {/* Main nav */}
      <nav style={{ flex: 1, padding: collapsed ? "10px 8px" : "12px 8px", overflowY: "auto" }}>
        {!collapsed && (
          <div
            style={{
              fontSize: 10,
              fontWeight: 600,
              color: COLORS.textLight,
              letterSpacing: "0.07em",
              textTransform: "uppercase",
              padding: "4px 10px 8px",
            }}
          >
            Main
          </div>
        )}

        {MAIN_NAV.map((item) => (
          <NavBtn key={item.id} {...item} />
        ))}

        <div
          style={{
            height: 1,
            background: COLORS.borderLight,
            margin: collapsed ? "10px 4px" : "12px 4px",
          }}
        />

        {!collapsed && (
          <div
            style={{
              fontSize: 10,
              fontWeight: 600,
              color: COLORS.textLight,
              letterSpacing: "0.07em",
              textTransform: "uppercase",
              padding: "4px 10px 8px",
            }}
          >
            Explore
          </div>
        )}

        {SECONDARY_NAV.map((item) => (
          <NavBtn key={item.id} {...item} />
        ))}

        <div
          style={{
            height: 1,
            background: COLORS.borderLight,
            margin: collapsed ? "10px 4px" : "12px 4px",
          }}
        />

        <button
          style={{
            display: "flex",
            alignItems: "center",
            gap: collapsed ? 0 : 10,
            justifyContent: collapsed ? "center" : "flex-start",
            width: "100%",
            padding: collapsed ? "9px 0" : "8px 10px",
            borderRadius: 6,
            border: "none",
            cursor: "pointer",
            background: "transparent",
            color: COLORS.textMuted,
            fontSize: 13.5,
            fontWeight: 400,
            textAlign: "left",
            whiteSpace: "nowrap",
          }}
          title={collapsed ? "Settings" : undefined}
        >
          <Icon name="settings" size={15} color={COLORS.textMuted} style={{ flexShrink: 0 }} />
          {!collapsed && "Settings"}
        </button>
      </nav>

      {/* User profile */}
      {!collapsed && (
        <div
          style={{
            padding: "12px 8px 16px",
            borderTop: `1px solid ${COLORS.borderLight}`,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "8px 10px",
              borderRadius: 6,
              background: COLORS.bg,
              border: `1px solid ${COLORS.borderLight}`,
            }}
          >
            <div
              style={{
                width: 30,
                height: 30,
                borderRadius: "50%",
                background: "#E0E7FF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 12,
                fontWeight: 600,
                color: COLORS.brand,
                flexShrink: 0,
              }}
            >
              U
            </div>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div
                style={{
                  fontSize: 13,
                  fontWeight: 500,
                  color: COLORS.text,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                Your Account
              </div>
              <div style={{ fontSize: 11, color: COLORS.textLight }}>Free plan</div>
            </div>
            <Icon
              name="log-out"
              size={13}
              color={COLORS.textLight}
              style={{ marginLeft: "auto", flexShrink: 0 }}
            />
          </div>
        </div>
      )}

      {collapsed && (
        <div
          style={{
            padding: "12px 0 16px",
            borderTop: `1px solid ${COLORS.borderLight}`,
            display: "flex",
            justifyContent: "center",
          }}
        >
          <div
            title="Account"
            style={{
              width: 30,
              height: 30,
              borderRadius: "50%",
              background: "#E0E7FF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 12,
              fontWeight: 600,
              color: COLORS.brand,
              cursor: "pointer",
            }}
          >
            U
          </div>
        </div>
      )}
    </div>
  );
};
