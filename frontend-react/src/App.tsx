import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { LoaderCircle, Search, Sparkles, X } from "lucide-react";

type SearchResult = {
  id: number;
  score: number;
  item_id: string;
  image_id: string;
  product_type: string;
  title: string;
  image_path: string;
  image_url: string;
};

type SearchResponse = {
  query: string;
  results: SearchResult[];
};

const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/$/, "");

const suggestions = [
  "rustic living room",
  "black handbag",
  "modern office setup",
  "warm neutral home decor",
  "blue phone case",
  "comfortable running shoes",
];

function App() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedResult, setSelectedResult] = useState<SearchResult | null>(
    null,
  );

  const searchInputRef = useRef<HTMLInputElement>(null);
  const activeRequest = useRef<AbortController | null>(null);
  const requestVersion = useRef(0);

  useEffect(() => {
    document.title = "ABO Visual Search";
  }, []);

  useEffect(() => {
    if (!selectedResult) return;

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setSelectedResult(null);
    };

    window.addEventListener("keydown", closeOnEscape);
    document.body.style.overflow = "hidden";

    return () => {
      window.removeEventListener("keydown", closeOnEscape);
      document.body.style.overflow = "";
    };
  }, [selectedResult]);

  const search = async (searchQuery: string) => {
    const cleanedQuery = searchQuery.trim();

    if (!cleanedQuery) {
      setError("Describe something you'd like to find.");
      searchInputRef.current?.focus();
      return;
    }

    activeRequest.current?.abort();

    const controller = new AbortController();
    const version = ++requestVersion.current;
    activeRequest.current = controller;

    setLoading(true);
    setError("");
    setSubmittedQuery(cleanedQuery);
    setResults([]);
    setSelectedResult(null);

    const timeout = window.setTimeout(() => controller.abort(), 30_000);

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: cleanedQuery,
          limit: 5,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Search failed with status ${response.status}.`);
      }

      const data: SearchResponse = await response.json();
      if (version !== requestVersion.current) return;

      setResults(data.results);
    } catch (requestError) {
      if (version !== requestVersion.current) return;

      if (
        requestError instanceof DOMException &&
        requestError.name === "AbortError"
      ) {
        setError("The search took too long. Please try again.");
      } else {
        setError(
          "Could not reach the search service. Check that the API is running.",
        );
      }
    } finally {
      window.clearTimeout(timeout);
      if (version === requestVersion.current) {
        setLoading(false);
      }
    }
  };

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void search(query);
  };

  const resetSearch = () => {
    activeRequest.current?.abort();
    requestVersion.current += 1;
    activeRequest.current = null;
    setLoading(false);
    setQuery("");
    setSubmittedQuery("");
    setResults([]);
    setError("");
    setSelectedResult(null);
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <button
          className="brand"
          type="button"
          onClick={resetSearch}
          aria-label="Return to search"
        >
          <span className="brand-mark" aria-hidden="true">
            <Search size={15} strokeWidth={1.8} />
          </span>
          <span>ABO Visual Search</span>
        </button>
        <span className="model-label">
          <span className="status-dot" />
          4,500 indexed images
        </span>
      </header>

      <main>
        <section
          className={`search-section ${
            submittedQuery ? "search-section--compact" : ""
          }`}
        >
          {!submittedQuery && (
            <div className="intro">
              <p className="eyebrow">SEMANTIC IMAGE SEARCH</p>
              <h1>Search products by meaning.</h1>
              <p className="intro-copy">
                Describe an object, style, color or use-case.
              </p>
            </div>
          )}

          <form className="search-form" onSubmit={submitSearch}>
            <Search
              className="search-icon"
              size={19}
              strokeWidth={1.8}
              aria-hidden="true"
            />

            <input
              ref={searchInputRef}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Try a black handbag..."
              aria-label="Search query"
            />

            <div className="search-actions">
              {query && (
                <button
                  type="button"
                  className="clear-button"
                  onClick={() => setQuery("")}
                  aria-label="Clear search"
                >
                  <X size={17} />
                </button>
              )}

              <button
                type="submit"
                className="submit-button"
                disabled={loading}
                aria-label="Search"
              >
                {loading ? (
                  <LoaderCircle className="spinner" size={18} />
                ) : (
                  <Search size={18} strokeWidth={1.8} />
                )}
              </button>
            </div>
          </form>

          {!submittedQuery && (
            <div className="suggestions">
              {suggestions.map((suggestion) => (
                <button
                  type="button"
                  key={suggestion}
                  onClick={() => {
                    setQuery(suggestion);
                    void search(suggestion);
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </section>

        {error && (
          <div className="notice" role="alert">
            {error}
          </div>
        )}

        {submittedQuery && !loading && results.length > 0 && (
          <section className="results-section" aria-live="polite">
            <div className="results-heading">
              <div>
                <p className="eyebrow">TOP 5 RESULTS</p>
                <h2>Matches for &ldquo;{submittedQuery}&rdquo;</h2>
              </div>
              <span>{results.length} images</span>
            </div>

            <div className="result-grid">
              {results.map((result, index) => (
                <article
                  className="result-card"
                  key={`${result.item_id}-${index}`}
                >
                  <button
                    type="button"
                    className="image-button"
                    onClick={() => setSelectedResult(result)}
                    aria-label={`Open ${result.title}`}
                  >
                    <img
                      src={result.image_url}
                      alt={result.title}
                      loading="lazy"
                      onError={(event) => {
                        event.currentTarget.onerror = null;
                        event.currentTarget.src =
                          "data:image/svg+xml;charset=UTF-8," +
                          encodeURIComponent(`
                            <svg xmlns="http://www.w3.org/2000/svg" width="600" height="700">
                              <rect width="100%" height="100%" fill="#e7e4dc"/>
                              <text x="50%" y="50%" text-anchor="middle"
                                fill="#77766f" font-family="sans-serif" font-size="18">
                                Image unavailable
                              </text>
                            </svg>
                          `);
                      }}
                    />

                    <span className="rank">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                  </button>

                  <div className="card-details">
                    <div>
                      <p className="category">
                        {result.product_type.replaceAll("_", " ").toLowerCase()}
                      </p>
                      <h3>{result.title}</h3>
                    </div>
                    <span className="score" title="Cosine similarity score">
                      {result.score.toFixed(3)}
                    </span>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {submittedQuery && !loading && results.length === 0 && !error && (
          <div className="empty-state">
            <Sparkles size={22} />
            <p>No matches found.</p>
            <p>Try a broader object or style description.</p>
          </div>
        )}

        {loading && (
          <div className="result-grid result-grid--loading">
            {[0, 1, 2, 3, 4].map((item) => (
              <div className="loading-card" key={item}>
                <div className="loading-image" />
                <div className="loading-line loading-line--short" />
                <div className="loading-line" />
              </div>
            ))}
          </div>
        )}
      </main>

      {selectedResult && (
        <div
          className="lightbox"
          role="dialog"
          aria-modal="true"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setSelectedResult(null);
            }
          }}
        >
          <button
            type="button"
            className="lightbox-close"
            onClick={() => setSelectedResult(null)}
            aria-label="Close"
          >
            <X size={20} />
          </button>

          <div className="lightbox-content">
            <img src={selectedResult.image_url} alt={selectedResult.title} />

            <div className="lightbox-details">
              <p className="category">
                {selectedResult.product_type.replaceAll("_", " ").toLowerCase()}
              </p>
              <h2>{selectedResult.title}</h2>
              <div className="lightbox-score">
                Match score
                <strong>{selectedResult.score.toFixed(3)}</strong>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
