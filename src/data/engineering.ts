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

export const fieldPhotos = [
  { file: 'streetlights-night', alt: 'A road at night lit by a line of working solar street lights', caption: 'Night-time functional check of an installed array' },
  { file: 'plinth-measurement', alt: 'A tape measure held against the concrete plinth at the base of a blue street-light pole', caption: 'Measuring a concrete plinth' },
  { file: 'pole-measurement', alt: 'A measuring tape wrapped around a blue galvanised street-light pole', caption: 'Checking pole dimensions' },
  { file: 'plinth-reinforcement', alt: 'Stacked steel reinforcement cages for street-light plinths', caption: 'Reinforcement cages for the plinths' },
  { file: 'earthing-installation', alt: 'An excavated plinth pit with reinforcement bars and a green earthing wire', caption: 'Earthing system during installation' },
  { file: 'unmounted-poles', alt: 'Rows of blue and white street-light poles laid on grass before installation', caption: 'Poles delivered before installation' },
];

export const siwes = {
  role: 'Industrial Trainee (SIWES)',
  department: 'Project Monitoring & Supervision (PMS) Department',
  org: 'Niger Delta Development Commission (NDDC)',
  orgNote: 'Rivers State Office · Federal Government development agency',
  period: 'July – December 2025',
  focus: 'Most of my field work was on solar street-light projects, which made up the largest share of active projects during my placement.',
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
      text: 'Observed and assisted on road inspections: length and width measurements with a measuring wheel and tape, checks of alignment, drainage and surface finish against the approved BEME, and records of deviations for corrective action.',
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
      text: 'I did not inspect the solar-powered water projects on site, but built working knowledge of them (geophysical and geotechnical surveys, borehole drilling, filtration, chlorination and UV treatment, elevated storage, gravity reticulation) through engineer briefings and BEME valuation work.',
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
  // From the final-year project report (Chapter 4). kg/day unless stated.
  meanDaily: { male: 4.133, female: 20.941 },
  sixDayTotal: { male: 24.8, female: 125.645, combined: 150.445 },
  share: { male: 16.48, female: 83.52 }, // % of the combined six-day total
  daily: [
    { label: 'Day 1', male: 8.95, female: 23.895 },
    { label: 'Day 2', male: 4.054, female: 27.75 },
    { label: 'Day 3', male: 2.03, female: 18.14 },
    { label: 'Day 4', male: 3.826, female: 17.15 },
    { label: 'Day 5', male: 2.68, female: 20.34 },
    { label: 'Day 6', male: 3.26, female: 18.37 },
  ],
  generation: { male: 0.041, female: 0.209 }, // kg/person/day
  composition: [
    { label: 'Plastics', male: 78.46, female: 80.46 },
    { label: 'Food', male: 5.1, female: 11.15 },
    { label: 'Cardboard', male: 6.06, female: 3.2 },
    { label: 'Paper', male: 3.48, female: 2.49 },
    { label: 'Residual', male: 2.72, female: 1.36 },
    { label: 'Metals', male: 2.4, female: 0.23 },
    { label: 'Glass', male: 0.76, female: 0.2 },
    { label: 'Dirt / soil', male: 0.61, female: 0.36 },
    { label: 'Yard', male: 0.42, female: 0.54 },
  ], // % by weight
  plastics: { male: 78.46, female: 80.46 },
  fractions: [
    { label: 'Biodegradable', male: 15.07, female: 17.39 },
    { label: 'Recyclable', male: 91.17, female: 86.58 },
    { label: 'Combustible', male: 96.27, female: 99.21 },
  ],
  // Estimated from standard literature values (Tchobanoglous et al., 1993) weighted by the
  // measured composition, not measured in a laboratory.
  physchem: [
    { label: 'Moisture content', unit: '%', male: '4.81', female: '8.77' },
    { label: 'Volatile matter', unit: '%', male: '84.28', female: '84.28' },
    { label: 'Carbon (ultimate analysis)', unit: '%', male: '54.74', female: '56.74' },
    { label: 'Heating value', unit: 'kJ/kg', male: '27,498.60', female: '27,758.31' },
    { label: 'Biological methane potential', unit: 'm³ CH₄/tonne', male: '7.110', female: '8.605' },
  ],
  formula: { male: 'C₂₉₂₄H₄₂₇₆O₉₇₇N₉S', female: 'C₂₅₂₂H₃₆₈₅O₈₄₃N₁₃S' },
  heatingValues: [27498.6, 27758.31], // kJ/kg, male then female
  gwp: { male: 21.388, female: 108.356, combined: 129.744 }, // kg CO2-eq over the study period
  ipcc: 'IPCC 2006 Tier 1 default method; MCF 0.4, DOC 0.15, DOCf 0.77, F 0.5, OX 0; GWP100 of 28 (IPCC AR5)',
  recommendations: {
    'University management': [
      'Labelled source-segregation bins for plastics, paper and cardboard, food waste and residual waste at hostel collection points.',
      'Scheduled hostel collection, prioritising high-generation hostels such as the female hostel.',
      'Composting or organic-waste diversion for the biodegradable fraction.',
      'Periodic waste audits across other hostels to build a campus-wide database.',
    ],
    'Government and regulators': [
      'A move from open dumping to managed disposal sites with gas control.',
      'Plastic recycling infrastructure that tertiary institutions can use.',
      'Environmental education on segregation, recycling and uncontrolled disposal.',
    ],
    'Students and residents': [
      'Separate plastics and food waste at source.',
      'Cut single-use packaging and disposable plastics where practicable.',
      'Take part in clean-up and waste-awareness initiatives.',
    ],
  },
  limitations: [
    'Six sampling days spread over two weeks (three days a week), so day-to-day and seasonal variation may not be fully captured.',
    'Twenty rooms per hostel (about 100 occupants) rather than the whole hostel population.',
    'Physicochemical properties, heating values, methane potential and emissions were estimated from standard literature values and IPCC defaults, not laboratory tests of the samples.',
    'Behavioural and dietary causes of the male–female difference were not investigated; the difference is reported as observed.',
    'Manual sorting and weighing carry a small risk of measurement or classification error.',
  ],
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
