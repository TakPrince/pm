"use client";

import { useEffect, useState, type FormEvent } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";

const AUTH_STORAGE_KEY = "pm-main-authenticated";
const AUTH_USERNAME_STORAGE_KEY = "pm-main-username";

export const LoginGate = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authenticatedUsername, setAuthenticatedUsername] = useState("user");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const storedAuth = sessionStorage.getItem(AUTH_STORAGE_KEY) === "true";
    const storedUsername = sessionStorage.getItem(AUTH_USERNAME_STORAGE_KEY) || "user";

    setIsAuthenticated(storedAuth);
    setAuthenticatedUsername(storedUsername);
  }, []);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (username === "user" && password === "password") {
      sessionStorage.setItem(AUTH_STORAGE_KEY, "true");
      sessionStorage.setItem(AUTH_USERNAME_STORAGE_KEY, username);
      setAuthenticatedUsername(username);
      setIsAuthenticated(true);
      setError("");
      return;
    }

    setError("Invalid username or password.");
  };

  const handleLogout = () => {
    sessionStorage.removeItem(AUTH_STORAGE_KEY);
    sessionStorage.removeItem(AUTH_USERNAME_STORAGE_KEY);
    setAuthenticatedUsername("user");
    setIsAuthenticated(false);
    setUsername("");
    setPassword("");
    setError("");
  };

  if (isAuthenticated) {
    return <KanbanBoard onLogout={handleLogout} username={authenticatedUsername} />;
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[var(--surface)] px-6 py-12">
      <section className="w-full max-w-[420px] border-t-4 border-[var(--accent-yellow)] bg-white p-8 shadow-[var(--shadow)]">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
          Project Board
        </p>
        <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--navy-dark)]">
          Sign in
        </h1>
        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <div>
            <label
              htmlFor="username"
              className="text-sm font-semibold text-[var(--navy-dark)]"
            >
              Username
            </label>
            <input
              id="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="mt-2 w-full border border-[var(--stroke)] px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
              autoComplete="username"
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="text-sm font-semibold text-[var(--navy-dark)]"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full border border-[var(--stroke)] px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
              autoComplete="current-password"
            />
          </div>
          {error ? (
            <p className="text-sm font-semibold text-[var(--secondary-purple)]">
              {error}
            </p>
          ) : null}
          <button
            type="submit"
            className="w-full bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold uppercase tracking-wide text-white transition hover:brightness-110"
          >
            Sign in
          </button>
        </form>
      </section>
    </main>
  );
};
