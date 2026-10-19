import type { PluginScreenProps } from "@getpaseo/plugin/client";
import { useRpc, usePaseo } from "@getpaseo/plugin/client";
import { useEffect, useMemo, useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { type BoardRow, observeBoard } from "../shared/board";
import { createFo } from "../shared/fo";
import { openCoordinator } from "../shared/coordinator";

interface WorkspaceChoice {
  id: string;
  repo: string;
  name: string;
}

function ago(iso: string): string {
  const seconds = Math.max(
    0,
    Math.round((Date.now() - Date.parse(iso)) / 1000),
  );
  if (seconds < 90) return `${seconds}s ago`;
  if (seconds < 5400) return `${Math.round(seconds / 60)}m ago`;
  return `${Math.round(seconds / 3600)}h ago`;
}

export function Board({ theme, layout, navigation }: PluginScreenProps) {
  const paseo = usePaseo();
  const callOpenCoordinator = useRpc(openCoordinator);
  const [rows, setRows] = useState<BoardRow[]>([]);
  const [workspaces, setWorkspaces] = useState<WorkspaceChoice[] | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let release: (() => void) | null = null;
    let cancelled = false;
    observeBoard(paseo, setRows).then(
      (stop) => (cancelled ? stop() : (release = stop)),
      (error) => setMessage(String(error)),
    );
    return () => {
      cancelled = true;
      release?.();
    };
  }, [paseo]);

  const colors = theme.colors;
  const styles = useMemo(
    () => ({
      screen: {
        flex: 1,
        padding: layout.compact ? 12 : 24,
        gap: 12,
        backgroundColor: colors.surface0,
      },
      bar: { flexDirection: "row" as const, gap: 8, flexWrap: "wrap" as const },
      button: { padding: 10, borderRadius: 8, backgroundColor: colors.accent },
      buttonText: { color: colors.accentForeground },
      row: {
        padding: 10,
        borderRadius: 8,
        backgroundColor: colors.surface1,
        gap: 2,
      },
      text: { color: colors.foreground },
      muted: { color: colors.foregroundMuted },
    }),
    [colors, layout.compact],
  );

  const statusColor = (status: BoardRow["status"]) =>
    status === "waiting on Kent"
      ? colors.statusWarning
      : status === "error"
        ? colors.statusDanger
        : status === "busy"
          ? colors.statusSuccess
          : colors.foregroundMuted;

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setMessage("");
    try {
      await action();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  const showWorkspaces = () =>
    run(async () => {
      const { entries } = await paseo.workspaces.list();
      setWorkspaces(
        entries.map((w) => ({
          id: w.id,
          repo: w.projectDisplayName,
          name: w.name,
        })),
      );
    });

  const startFo = (choice: WorkspaceChoice) =>
    run(async () => {
      const agentId = await createFo(paseo, {
        workspaceId: choice.id,
        repo: choice.repo,
      });
      setWorkspaces(null);
      navigation?.openAgent({ agentId });
    });

  const openCoordinatorAgent = () =>
    run(async () => {
      const { agentId } = await callOpenCoordinator({});
      navigation?.openAgent({ agentId });
    });

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <View style={styles.bar}>
        <Pressable
          accessibilityRole="button"
          disabled={busy}
          onPress={() => void showWorkspaces()}
          style={styles.button}
        >
          <Text style={styles.buttonText}>New FO</Text>
        </Pressable>
        <Pressable
          accessibilityRole="button"
          disabled={busy}
          onPress={() => void openCoordinatorAgent()}
          style={styles.button}
        >
          <Text style={styles.buttonText}>Open coordinator</Text>
        </Pressable>
      </View>
      {message ? (
        <Text style={{ color: colors.statusDanger }}>{message}</Text>
      ) : null}
      {workspaces ? (
        <View style={styles.row}>
          <Text style={styles.muted}>Start an FO in:</Text>
          {workspaces.map((w) => (
            <Pressable
              key={w.id}
              accessibilityRole="button"
              disabled={busy}
              onPress={() => void startFo(w)}
            >
              <Text style={styles.text}>
                {w.repo} / {w.name}
              </Text>
            </Pressable>
          ))}
        </View>
      ) : null}
      {rows.length === 0 ? (
        <Text style={styles.muted}>No agents labelled role=fo.</Text>
      ) : null}
      {rows.map((row) => (
        <Pressable
          key={row.id}
          accessibilityRole="button"
          onPress={() => navigation?.openAgent({ agentId: row.id })}
          style={styles.row}
        >
          <Text style={styles.text}>
            {row.repo || "(no repo label)"} - {row.task || "(no task label)"}
          </Text>
          <Text style={{ color: statusColor(row.status) }}>
            {row.status} - {ago(row.lastActivityAt)}
          </Text>
        </Pressable>
      ))}
    </ScrollView>
  );
}
