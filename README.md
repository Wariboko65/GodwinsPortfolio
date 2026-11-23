# John Godwin Oamien: personal website

One personal website with two professional profiles:

- **`/software`**: frontend / full stack developer portfolio
- **`/engineering`**: Civil & Environmental Engineering profile

The start page (`/`) introduces me and lets visitors choose a path. Every page links back to the start page and across to the other profile. The last profile a visitor opened is remembered (in `localStorage`) and offered on the start page.

Live: https://godwins-portfolio.vercel.app

## Stack

- [Astro](https://astro.build) 7, static output, no client framework
- Plain CSS with design tokens (`src/styles/global.css`) and component-scoped styles
- Self-hosted variable fonts via Fontsource: Schibsted Grotesk, Newsreader, JetBrains Mono
- `astro:assets` for responsive AVIF/WebP images
- A generated `/sitemap.xml` (`src/pages/sitemap.xml.ts`) that lists every page automatically

JavaScript on the page is limited to: scroll reveals (skipped when reduced motion is requested, and content is visible without JS), remembering the chosen path, and the contact form.

## Commands

| Command           | What it does                         |
| ----------------- | ------------------------------------ |
| `npm install`     | Install dependencies (Node 20+)      |
| `npm run dev`     | Local dev server at `localhost:4321` |
| `npm run build`   | Build the static site into `dist/`   |
| `npm run preview` | Serve the built site locally         |

## Where things live

```
src/
  data/
    site.ts          Name, contact details, CV paths, navigation for each profile
    software.ts      Case studies, stack map, experience, Frontend Mentor archive
    engineering.ts   Degree, SIWES duties, final-year study figures, knowledge areas
  layouts/
    Base.astro       <head>, SEO and Open Graph tags, shared scripts
    Profile.astro    Header (name, nav, profile switch) and footer for both profiles
  components/        ContactForm, ContactSection, CaseHeader, CaseNext,
                     PairChart (study charts), TitleBlock, Contours
  pages/             One file per route (see below)
  assets/
    photos/          Portraits (EXIF/location data stripped)
    field/           SIWES inspection photos and study photos (overlays cropped)
    projects/        Project screenshots, cropped to 16:10
public/
  cv/                Software and engineering CVs (PDF)
  og/                Open Graph images for /, /software and /engineering
```

### Routes

```
/                                          Start page and path choice
/software                                  Developer overview
/software/about
/software/projects
/software/projects/jopad-advisory          Case study
/software/projects/jason                   Case study
/software/projects/vortex-horizon          Case study
/software/projects/frontend-mentor         Archive (14 solutions)
/software/contact
/engineering                               Engineering overview
/engineering/about
/engineering/education
/engineering/projects
/engineering/projects/hostel-solid-waste-study   Final-year research
/engineering/contact
```

## Editing content

- **Contact details, CV files, nav:** `src/data/site.ts`.
- **Add a Frontend Mentor project:** add a screenshot to `src/assets/projects/`, import it at the top of `src/data/software.ts`, and add an entry to the right group in `archive`. Only list tech that is actually in the repo.
- **Engineering coursework:** `coursework` in `src/data/engineering.ts` is empty on purpose. The Education page shows a "Relevant coursework" section as soon as confirmed course titles are added.
- **Engineering figures and photos:** study figures come from the final-year project report (Chapter 4) and field photos from the SIWES report, both cropped to remove GPS-camera overlays. Photos showing identifiable people (handover meetings, hostel residents) are deliberately not used, and the water-scheme photos are left out because those projects were not inspected in person. Physicochemical values are literature-based estimates and are labelled as such.
- **Case study screenshots:** JOPAD and Jason have no screenshots yet. To add one, put the image in `src/assets/projects/` and render it with `<Picture>` as the Vortex Horizon page does.

Accuracy rules for the copy: JOPAD's frontend is vanilla HTML/CSS/JavaScript (not React); the backend is Node.js/Express/MongoDB. Jason is React + TypeScript. Engineering figures come only from the engineering CV. Do not add metrics or outcomes that are not documented.

## Contact form

Both contact pages post to the existing Google Apps Script endpoint (`site.formEndpoint`) with the fields `Name`, `Email` and `Message`, which match the existing Google Sheet. A hidden `Profile` field (`Software` / `Engineering`) is also sent. It is saved only if the sheet has a column with that header, so add a `Profile` column to see which profile each message came from. A honeypot field filters simple bots on the client.

## Deployment (Vercel)

`vercel.json` pins the framework to Astro, the build command to `npm run build` and the output directory to `dist`. This matters because the repository used to be a plain static site with no build step. It also:

- redirects `/Images/Godwin_Resume.pdf` (the old CV link) to the new software CV
- redirects the old `/sitemap-index.xml` and `/sitemap-0.xml` to `/sitemap.xml`; submit `https://godwins-portfolio.vercel.app/sitemap.xml` in Search Console
- sets long-lived caching for hashed assets in `/_astro/`

The Google Search Console verification tag is kept on the start page.
