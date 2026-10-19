import type {
  PluginClientContext,
  PluginSidebarItemProps,
} from "@getpaseo/plugin/client";
import { SidebarRow } from "@getpaseo/plugin/client/ui";
import { Board } from "./client/board";

function BoardItem({ currentScreen, openScreen }: PluginSidebarItemProps) {
  return (
    <SidebarRow
      icon="Users"
      label="FO board"
      active={currentScreen?.screenId === "board"}
      onPress={() => openScreen({ screenId: "board" })}
    />
  );
}

export default function contribute(client: PluginClientContext) {
  client.addScreen({ id: "board", title: "FO board", Component: Board });
  client.addSidebarHeaderItem({
    id: "board",
    title: "FO board",
    Component: BoardItem,
  });
  return () => {};
}
