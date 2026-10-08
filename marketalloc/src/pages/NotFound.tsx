import { Link } from "react-router-dom";

export default function NotFound() {
  return <main className="content-wrap not-found"><p className="eyebrow">PAGE NOT FOUND</p><h1>This page is not available.</h1><p>Return to the overview or upload a marketing dataset to continue.</p><Link className="button button-accent" to="/">Back to MARKETALLOC</Link></main>;
}
