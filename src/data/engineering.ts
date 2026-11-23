// Every figure here comes from the engineering CV (public/cv/john-godwin-oamien-engineering-cv.pdf).
// Do not add results, coursework or experience that is not documented there.

export const degree = {
  title: 'Bachelor of Engineering (B.Eng.)',
  programme: 'Civil and Environmental Engineering',
  option: 'Environmental Engineering option',
  institution: 'University of Port Harcourt',
  place: 'Rivers State, Nigeria',
  years: '2020 – 2026',
  status: 'Final-year project defended in 2026',
};

// Leave empty until confirmed course titles are available; the Education page hides the
// section while this list is empty.
export const coursework: string[] = [];

export const siwes = {
  role: 'Industrial Trainee (SIWES)',
  department: 'Project Monitoring & Supervision (PMS) Department',
  org: 'Niger Delta Development Commission (NDDC)',
  orgNote: 'Rivers State Office · Federal Government development agency',
  period: 'July – December 2025',
  duties: [
    {
      title: 'Site handovers',
      text: 'Supported handover exercises for emergency solar street-light projects. I recorded project details and community concerns, documented NDDC, contractor and community-leader attendance with photographs, and helped complete and file Site Handover Forms.',
    },
    {
      title: 'Field inspection',
      text: 'Assisted inspections of 100 W all-in-one solar street lights: pole and 450 × 450 × 1000 mm concrete plinth dimensions, compaction and alignment, earthing rod and copper-wire connections, finishing and signposts. Installed units were reconciled against BEME quantities and confirmed working through night-time checks.',
    },
    {
      title: 'Road works monitoring',
      text: 'Took length and width measurements with a measuring wheel and tape, checked alignment, drainage and surface finish against the approved BEME, and documented deviations for corrective action.',
    },
    {
      title: 'Valuation',
      text: 'Assisted valuation of completed road, solar street-light, solar-powered water and building projects: reviewing BEME provisions, computing quantities and costs with standard templates, and cross-checking figures against inspection records.',
    },
    {
      title: 'Documentation',
      text: 'Compiled Performance Evaluation Forms, inspection checklists, reports and memos recording installed items, dimensions, defects and compliance status, and kept project files and photographic evidence in order.',
    },
    {
      title: 'Technical exposure',
      text: 'Built working knowledge of solar-powered water schemes (geophysical and geotechnical surveys, borehole drilling, filtration, chlorination and UV treatment, elevated GRP storage, gravity reticulation) through BEME study and engineer briefings.',
    },
  ],
};

export const study = {
  slug: 'hostel-solid-waste-study',
  title: 'Solid Waste Generation and Characterization in Selected Male and Female Hostels',
  short: 'Hostel solid waste study',
  type: 'B.Eng. final-year research project',
  year: '2026',
  site: 'Rivers State University',
  supervisor: 'Dr. Momoh Yusuf',
  design: {
    hostels: [
      { name: 'Hostel E', group: 'Male' },
      { name: 'Hostel D', group: 'Female' },
    ],
    roomsPerHostel: 20,
    occupantsPerHostel: 100,
    samplingDays: 6,
    totalKg: 150.4,
    categories: 9,
  },
  generation: { male: 0.041, female: 0.209 }, // kg/person/day
  plastics: { male: 78.5, female: 80.5 }, // % by weight
  fractions: [
    { label: 'Biodegradable', male: 15.1, female: 17.4 },
    { label: 'Recyclable', male: 91.2, female: 86.6 },
    { label: 'Combustible', male: 96.3, female: 99.2 },
  ],
  heatingValues: [27500, 27760], // kJ/kg, approximate
  gwp: { male: 21.4, female: 108.4, combined: 129.7 }, // kg CO2-eq over the study period
};

export const knowledge = [
  {
    area: 'Environmental & waste engineering',
    basis: 'Final-year research',
    items: [
      'Solid waste sampling and characterisation',
      'Waste generation rate analysis',
      'Integrated Solid Waste Management (ISWM)',
      'Waste hierarchy and circular economy',
      'Waste-to-energy and methane potential',
      'GHG and GWP estimation (IPCC Tier 1)',
      'Field safety and PPE practice',
    ],
  },
  {
    area: 'Civil works & project monitoring',
    basis: 'SIWES at NDDC',
    items: [
      'Site handover procedures',
      'Field inspection and quality control',
      'BEME interpretation',
      'Quantity measurement and valuation',
      'Road works and flexible pavement stages',
      'Foundation and plinth checks',
      'Specification compliance',
    ],
  },
  {
    area: 'Sustainable infrastructure',
    basis: 'Working knowledge from SIWES',
    items: [
      'Solar street-lighting systems',
      'Solar-powered water supply',
      'Water treatment and reticulation fundamentals',
      'Groundwater development (geotechnical and geophysical surveys)',
    ],
  },
  {
    area: 'Tools',
    basis: 'Level as stated on my CV',
    items: [
      'Microsoft Excel (intermediate)',
      'ArcGIS (basic)',
      'Word and PowerPoint (proficient)',
      'Measuring wheel and tape',
      'Digital weighing scale',
    ],
  },
];

export const strengths = [
  'Technical report writing',
  'Data tabulation and comparative analysis',
  'Photographic documentation',
  'Records management',
  'Stakeholder and community engagement',
];
