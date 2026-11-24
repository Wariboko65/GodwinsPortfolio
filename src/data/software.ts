import type { ImageMetadata } from 'astro';
import nft from '../assets/projects/nft-preview.png';
import orderSummary from '../assets/projects/order-summary.png';
import threeColumn from '../assets/projects/three-column.png';
import chat from '../assets/projects/chat-illustration.png';
import testimonials from '../assets/projects/testimonials-grid.png';
import fylo from '../assets/projects/fylo-storage.png';
import clipboard from '../assets/projects/clipboard.png';
import huddle from '../assets/projects/huddle.png';
import newsletter from '../assets/projects/newsletter.png';
import multiStep from '../assets/projects/multi-step-form.png';
import calculator from '../assets/projects/calculator.png';
import advice from '../assets/projects/advice-generator.png';
import conference from '../assets/projects/conference-ticket.png';
import extensions from '../assets/projects/extensions-manager.png';

/* ------------------------------------------------------------------ */
/* Case studies                                                        */
/* ------------------------------------------------------------------ */

export const caseStudies = [
  {
    slug: 'jopad-advisory',
    name: 'JOPAD Advisory',
    kind: 'Contract · Full stack',
    year: '2026',
    summary:
      'A consulting and booking platform for Jogos Partners & Advisory LP. Clients book a consultation, the server checks the slot, and the calendar invite, Meet link and confirmation emails go out without anyone touching them.',
    stack: ['HTML', 'CSS', 'JavaScript', 'Node.js', 'Express', 'MongoDB', 'Google Calendar API'],
    live: 'https://jopadconsulting.com/',
  },
  {
    slug: 'jason',
    name: 'Jason',
    kind: 'Contract · Frontend',
    year: null,
    summary:
      'A fundraising site for a child’s corrective surgery. It shows campaign progress, keeps the family’s bank details behind an explicit confirmation step, and makes sharing the appeal a single tap.',
    stack: ['React', 'TypeScript', 'Zustand', 'Framer Motion'],
    live: 'https://jason-orpin.vercel.app/',
  },
  {
    slug: 'vortex-horizon',
    name: 'Vortex Horizon',
    kind: 'Concept project · Frontend',
    year: '2022',
    summary:
      'A concept website for an imaginary web and 3D studio, built to practise a complete multi-section site: services, a filterable work gallery, light and dark themes, and a contact form that writes straight into a Google Sheet. Plain HTML, CSS and JavaScript.',
    stack: ['HTML', 'CSS', 'JavaScript', 'Google Apps Script'],
    live: 'https://vortexhorizon.vercel.app/',
    repo: 'https://github.com/wariboko65/Vortex_Horizon',
  },
] as const;

/* ------------------------------------------------------------------ */
/* Stack map: tools grouped by layer, with where each one was used.   */
/* Only list a project when the repo, CV or brief confirms it.        */
/* ------------------------------------------------------------------ */

export const stack = [
  {
    layer: 'Interface',
    tools: ['HTML5', 'CSS3', 'Sass', 'JavaScript', 'TypeScript', 'React', 'Tailwind CSS', 'Bootstrap'],
    usedIn: 'JOPAD (vanilla JS), Jason (React + TypeScript), Frontend Mentor solutions (Sass, React)',
  },
  {
    layer: 'State & motion',
    tools: ['Zustand', 'Framer Motion', 'localStorage'],
    usedIn: 'Jason, Browser Extensions Manager',
  },
  {
    layer: 'Server & data',
    tools: ['Node.js', 'Express', 'REST APIs', 'MongoDB', 'Mongoose'],
    usedIn: 'JOPAD booking, leads and articles APIs',
  },
  {
    layer: 'Integrations',
    tools: ['Google Calendar API', 'OAuth2', 'Google Meet', 'Resend', 'Airtable', 'Google Apps Script'],
    usedIn: 'JOPAD; Google Sheets forms on Vortex Horizon and this site',
  },
  {
    layer: 'Shipping',
    tools: ['Git', 'GitHub', 'Vercel', 'Render', 'GA4', 'Search Console', 'DevTools'],
    usedIn: 'Every project; Render and GA4 on JOPAD',
  },
] as const;

export const experience = [
  {
    period: '2026',
    title: 'Full Stack Developer (contract)',
    org: 'Jogos Partners & Advisory LP (JOPAD Advisory)',
    note: 'Booking platform, lead intake, articles CMS, SEO and production deployment.',
    href: '/software/projects/jopad-advisory',
  },
  {
    period: 'Contract',
    title: 'Frontend Developer',
    org: 'Jason medical fundraising campaign',
    note: 'React and TypeScript campaign site with progress tracking and a privacy-gated donation flow.',
    href: '/software/projects/jason',
  },
  {
    period: '2020 – present',
    title: 'Self-taught developer',
    org: 'Frontend Mentor and independent study',
    note: 'Fourteen published solutions, from CSS components to React apps.',
    href: '/software/projects/frontend-mentor',
  },
] as const;

export const certification = {
  name: 'Advanced JavaScript & Modern Frontend Frameworks',
  issuer: 'micro1',
  detail: 'React, Vue and Angular',
};

/* ------------------------------------------------------------------ */
/* Frontend Mentor archive                                             */
/* Tech is taken from the files in each GitHub repository.            */
/* ------------------------------------------------------------------ */

export type ArchiveItem = {
  name: string;
  blurb: string;
  tech: string[];
  image: ImageMetadata;
  live: string;
  repo: string;
  solution?: string;
};

const gh = (r: string) => `https://github.com/wariboko65/${r}`;

export const archive: { group: string; intro: string; items: ArchiveItem[] }[] = [
  {
    group: 'Applications',
    intro: 'State, validation, routing and data from an API.',
    items: [
      {
        name: 'Browser Extensions Manager',
        blurb:
          'Filter extensions by status, toggle and remove them, switch themes. Choices persist in localStorage and removals go through a modal built with React portals.',
        tech: ['React', 'Vite', 'React Router', 'Framer Motion'],
        image: extensions,
        live: 'https://browser-extension-nu-six.vercel.app/',
        repo: gh('BrowserExtension'),
        solution:
          'https://www.frontendmentor.io/solutions/browser-extension-manager-ui-using-react-and-css-variables-LysCCS-s0_',
      },
      {
        name: 'Conference Ticket Generator',
        blurb:
          'A form with avatar upload and inline validation that turns the entries into a personalised conference ticket.',
        tech: ['React', 'Vite', 'React Router'],
        image: conference,
        live: 'https://conference-ticket-generator-steel-eight.vercel.app/',
        repo: gh('Conference-Ticket-Generator'),
        solution: 'https://www.frontendmentor.io/solutions/conference-ticket-generator-H8Cb7Y-NJs',
      },
      {
        name: 'Multi-step Form',
        blurb: 'A four-step subscription sign-up with per-step validation, plan toggles and a live summary.',
        tech: ['HTML', 'CSS', 'JavaScript'],
        image: multiStep,
        live: 'https://multi-step-form-wine-six.vercel.app/',
        repo: gh('Multi-step-form'),
        solution:
          'https://www.frontendmentor.io/solutions/html-css-javascript-responsive-development-mobile-first-dev-a6loyzNSkB',
      },
      {
        name: 'Calculator App',
        blurb: 'A working calculator with three switchable colour themes.',
        tech: ['HTML', 'CSS', 'JavaScript'],
        image: calculator,
        live: 'https://calculator-app-iota-flax.vercel.app/',
        repo: gh('Calculator-app'),
        solution: 'https://www.frontendmentor.io/solutions/html-css-javascript-responsive-design-v135_tbD-Y',
      },
      {
        name: 'Advice Generator',
        blurb: 'Fetches a random piece of advice from the Advice Slip API on each click.',
        tech: ['HTML', 'Sass', 'JavaScript', 'REST API'],
        image: advice,
        live: 'https://advice-generator-app-seven-sooty.vercel.app/',
        repo: gh('Advice-generator-app'),
        solution: 'https://www.frontendmentor.io/solutions/advice-generator-app-LQ_ph2yOt2',
      },
    ],
  },
  {
    group: 'Landing pages',
    intro: 'Full responsive pages built from a design file.',
    items: [
      {
        name: 'Newsletter Sign-up',
        blurb: 'Email validation with an error state and a success screen.',
        tech: ['HTML', 'CSS', 'JavaScript'],
        image: newsletter,
        live: 'https://news-letter-success-message.vercel.app/',
        repo: gh('news_letter_success_message'),
        solution: 'https://www.frontendmentor.io/solutions/newslettersuccessmessage-16Qvmye8ae',
      },
      {
        name: 'Clipboard Landing Page',
        blurb: 'A long product landing page with feature sections and a responsive grid.',
        tech: ['HTML', 'Sass'],
        image: clipboard,
        live: 'https://clipboard-landing-page-zeta-six.vercel.app/',
        repo: gh('clipboard-landing-page'),
      },
      {
        name: 'Huddle Landing Page',
        blurb: 'Curved section dividers that hold their shape from mobile to desktop.',
        tech: ['HTML', 'CSS'],
        image: huddle,
        live: 'https://huddle-landing-page-with-curved-sections-puce.vercel.app/',
        repo: gh('huddle-landing-page-with-curved-sections'),
      },
    ],
  },
  {
    group: 'Components',
    intro: 'Where I started: layout, spacing and getting the details right.',
    items: [
      {
        name: 'Testimonials Grid',
        blurb: 'An asymmetric CSS Grid layout that collapses cleanly to one column.',
        tech: ['HTML', 'CSS'],
        image: testimonials,
        live: 'https://testimonials-grid-section-main-murex-eight.vercel.app/',
        repo: gh('testimonials-grid-section-main'),
      },
      {
        name: 'Fylo Data Storage',
        blurb: 'A storage-usage widget with a gradient progress meter.',
        tech: ['HTML', 'CSS'],
        image: fylo,
        live: 'https://fylo-data-storage-component-master-woad-ten.vercel.app/',
        repo: gh('fylo-data-storage-component-master'),
      },
      {
        name: 'Chat App Illustration',
        blurb: 'A phone mock-up and chat interface drawn entirely in CSS.',
        tech: ['HTML', 'CSS'],
        image: chat,
        live: 'https://chat-app-css-illustration-master-azure.vercel.app/',
        repo: gh('chat-app-css-illustration-master'),
      },
      {
        name: 'Order Summary Card',
        blurb: 'A checkout summary card with plan details and actions.',
        tech: ['HTML', 'Sass'],
        image: orderSummary,
        live: 'https://order-summary-component-main-six-mu.vercel.app/',
        repo: gh('order-summary-component-main'),
        solution: 'https://www.frontendmentor.io/solutions/csshtmlsass-s7YEdJo6N2',
      },
      {
        name: 'NFT Preview Card',
        blurb: 'A product card with an image hover overlay.',
        tech: ['HTML', 'Sass'],
        image: nft,
        live: 'https://nft-preview-card-component-main-sable.vercel.app/',
        repo: gh('nft-preview-card-component-main'),
        solution: 'https://www.frontendmentor.io/solutions/css-sass-qHYyQrhWVW',
      },
      {
        name: '3-Column Preview Card',
        blurb: 'Three joined cards that stack vertically on small screens.',
        tech: ['HTML', 'Sass'],
        image: threeColumn,
        live: 'https://3-column-preview-card-component-main-brown-three.vercel.app/',
        repo: gh('3-column-preview-card-component-main'),
      },
    ],
  },
];

export const archiveCount = archive.reduce((n, g) => n + g.items.length, 0);
