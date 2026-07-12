import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData } from "@/lib/kanban";

const mockFetch = vi.fn();

beforeEach(() => {
  mockFetch.mockReset();
  vi.stubGlobal("fetch", mockFetch);
});

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  it("renders five columns", () => {
    render(<KanbanBoard />);
    expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("loads the board from the backend on mount", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ...initialData,
        columns: [{ ...initialData.columns[0], title: "Loaded from API" }, ...initialData.columns.slice(1)],
      }),
    });

    render(<KanbanBoard username="user" />);

    expect(screen.getByText(/loading board/i)).toBeInTheDocument();
    expect(await screen.findByText("Loaded from API")).toBeInTheDocument();
  });

  it("renames a column", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => initialData,
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    render(<KanbanBoard username="user" />);
    await waitFor(() => expect(screen.queryByText(/loading board/i)).not.toBeInTheDocument());
    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    await waitFor(() => expect(input).toHaveValue("New Name"));
  });

  it("persists board changes to the backend", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => initialData,
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    render(<KanbanBoard username="user" />);
    await waitFor(() => expect(screen.queryByText(/loading board/i)).not.toBeInTheDocument());
    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");

    await userEvent.clear(input);
    await userEvent.type(input, "New Name");

    await waitFor(() => {
      const saveCalls = mockFetch.mock.calls.filter(
        ([url, options]) => url === "/api/board?username=user" && options?.method === "PUT"
      );

      expect(saveCalls.length).toBeGreaterThan(0);
    });
  });

  it("adds and removes a card", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => initialData,
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    render(<KanbanBoard />);
    await waitFor(() => expect(screen.queryByText(/loading board/i)).not.toBeInTheDocument());
    const column = getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });
});
