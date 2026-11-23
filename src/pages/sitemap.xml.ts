// Single sitemap at /sitemap.xml, generated from the page files on every build,
// so new pages are included automatically. Submit this URL in Google Search Console.
import type { APIRoute } from 'astro';
import { site } from '../data/site';

const pages = import.meta.glob('./**/*.astro');

export const GET: APIRoute = () => {
  const lastmod = new Date().toISOString().slice(0, 10);
  const paths = Object.keys(pages)
    .map((f) => f.replace(/^\.\//, '/').replace(/\.astro$/, '').replace(/\/index$/, '') || '/')
    .filter((p) => p !== '/404' && !p.includes('['))
    .sort((a, b) => a.split('/').length - b.split('/').length || a.localeCompare(b));

  const priority = (p: string) => (p === '/' ? '1.0' : p === '/software' || p === '/engineering' ? '0.9' : p.includes('/projects/') ? '0.7' : '0.8');

  const body =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    paths
      .map(
        (p) =>
          `  <url>\n    <loc>${new URL(p, site.url).href.replace(/\/$/, p === '/' ? '/' : '')}</loc>\n    <lastmod>${lastmod}</lastmod>\n    <priority>${priority(p)}</priority>\n  </url>`,
      )
      .join('\n') +
    '\n</urlset>\n';

  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
