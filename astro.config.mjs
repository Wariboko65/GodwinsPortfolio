// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://godwins-portfolio.vercel.app',
  trailingSlash: 'never',
  build: { format: 'directory' },
});
