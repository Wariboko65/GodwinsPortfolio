// Shared identity and contact details. Edit here and every page updates.

export const person = {
  fullName: 'John Godwin Oamien',
  location: 'Port Harcourt, Rivers State, Nigeria',
  email: 'oamienjoh20034@gmail.com',
  phoneDisplay: '+234 814 165 7601',
  phoneHref: 'tel:+2348141657601',
  whatsapp: 'https://wa.me/2348141657601',
  linkedin: 'https://www.linkedin.com/in/godwin-john-920915206',
  github: 'https://github.com/wariboko65',
  frontendMentor: 'https://www.frontendmentor.io/profile/wariboko65',
  telegram: 'https://t.me/Gdwin656',
};

export const site = {
  url: 'https://godwins-portfolio.vercel.app',
  // Existing Google Apps Script endpoint that writes contact messages to a Google Sheet.
  formEndpoint:
    'https://script.google.com/macros/s/AKfycbymenROw-xordeZtvMS0kc0iD8z_NkB2wNW_m0TyY5VpJMjYfWMXVmyjwL0GTGRbY8M2w/exec',
  googleVerification: 'SW0lxBOB1ZcnnW01LjCnPgsuOrlc0CoaYZuhtxVj8i8',
  cv: {
    software: '/cv/john-godwin-oamien-software-cv.pdf',
    engineering: '/cv/john-godwin-oamien-engineering-cv.pdf',
  },
};

export type Path = 'software' | 'engineering';

export const paths = {
  software: {
    label: 'Software Development',
    short: 'Software',
    role: 'Frontend / Full Stack Developer',
    home: '/software',
    nav: [
      { href: '/software', label: 'Overview' },
      { href: '/software/projects', label: 'Projects' },
      { href: '/software/about', label: 'About' },
      { href: '/software/contact', label: 'Contact' },
    ],
  },
  engineering: {
    label: 'Civil & Environmental Engineering',
    short: 'Engineering',
    role: 'B.Eng. Civil & Environmental Engineering',
    home: '/engineering',
    nav: [
      { href: '/engineering', label: 'Overview' },
      { href: '/engineering/projects', label: 'Projects' },
      { href: '/engineering/education', label: 'Education' },
      { href: '/engineering/about', label: 'About' },
      { href: '/engineering/contact', label: 'Contact' },
    ],
  },
} as const;
