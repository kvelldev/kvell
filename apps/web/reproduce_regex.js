
const ALLOWLIST_PATTERNS = [
  /^https?:\/\/(?:Basic\.)?sakurazaka46\.com\/.*(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)/i,
];

const url = "https://sakurazaka46.com/images/14/1da/cc4ad523f0f498a55f87970859bec.jpg";

let matched = false;
for (const pattern of ALLOWLIST_PATTERNS) {
  if (pattern.test(url)) {
    console.log("Matched!", pattern);
    matched = true;
    break;
  }
}

if (!matched) {
  console.log("No match found.");
}
