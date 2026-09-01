// Build a credits block for a spot from the C41 CRM, for when neither the
// masters folder nor Instagram has one.
//
//   cd ~/dev/CRM/c41-app
//   node --env-file=.env.local ~/dev/nrm461.github.io/_build/crm_credits.mjs "Hills" \
//        --client "Hill's Pet Nutrition" --title "Try Again" > /tmp/credits.txt
//
// Emits the same shape the site's `credits` field already uses, so it can be
// handed to add_spot.py with --credits-file. Only the roles we actually know
// go in — a partial block is the point.
import { query } from '/Users/nickmetcalf/dev/CRM/c41-app/lib/db.js';

const args = process.argv.slice(2);
const search = args.find(a => !a.startsWith('--'));
const flag = n => { const i = args.indexOf('--' + n); return i >= 0 ? args[i + 1] : null; };

if (!search) {
  console.error('usage: crm_credits.mjs <job search> [--client X] [--title Y] [--job-number N]');
  process.exit(1);
}

// CRM role -> the label the site's credit blocks use. Order is the output order.
const ROLES = [
  [/^director$/i, 'Director'],
  [/^(dp|dop|cinematographer)$/i, 'DP'],
  [/^editor$/i, 'Edit'],
];

const num = flag('job-number');
const jobs = num
  ? await query(`select id, job_number, title from jobs where job_number = $1`, [num])
  : await query(`select id, job_number, title from jobs where title ilike $1
                 order by year desc nulls last`, [`%${search}%`]);

if (!jobs.length) {
  console.error(`no job matching "${num ?? search}"`);
  process.exit(1);
}
if (jobs.length > 1 && !num) {
  console.error(`"${search}" matches ${jobs.length} jobs — pick one with --job-number:`);
  for (const j of jobs) console.error(`   ${j.job_number ?? '(none)'}  ${j.title}`);
  process.exit(1);
}

const job = jobs[0];
const people = await query(
  `select c.name, c.title as role, c.instagram, co.name as company, co.kind as company_kind
   from job_contacts jc
   join contacts c on c.id = jc.contact_id
   left join companies co on co.id = c.company_id
   where jc.job_id = $1`, [job.id]);

// A bare handle becomes @handle; anything else falls back to the plain name.
const credit = p => {
  const h = (p.instagram ?? '').trim();
  return /^[A-Za-z0-9._]{1,30}$/.test(h) ? '@' + h : p.name.replace(/\s*\(.*?\)\s*/g, '').trim();
};

const lines = [];
lines.push(flag('client') ?? job.title);
lines.push(flag('title') ?? '');
lines.push('');

let found = 0;
for (const [re, label] of ROLES) {
  const hits = people.filter(p => re.test((p.role ?? '').trim()));
  if (!hits.length) continue;
  found += hits.length;
  lines.push(`${label}: ${hits.map(credit).join(', ')}`);
}
lines.push('Color: @nick__metcalf @raremedium.tv');

// Only a company actually typed as a production company — a contact's employer
// is often the edit house, which is a different credit.
const prod = people.find(p => p.company && p.company_kind === 'prod_co');
const viaJob = prod ? null : await query(
  `select co.name from job_companies jco join companies co on co.id = jco.company_id
   where jco.job_id = $1 and co.kind = 'prod_co' limit 1`, [job.id]);
const prodName = prod?.company ?? viaJob?.[0]?.name;
if (prodName) lines.push(`Production: ${prodName}`);

console.error(`-- ${job.title} (${job.job_number ?? 'no number'}): ${found} of ` +
              `${people.length} contacts matched a credited role`);
console.log(lines.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n');

process.exit(0);
