const cards = [...document.querySelectorAll("[data-pet]")];
const grid = document.querySelector("#grid");
const chips = [...document.querySelectorAll("[data-filter]")];
const search = document.querySelector("#q");
const sort = document.querySelector("#sort");
const count = document.querySelector("#count");
const empty = document.querySelector("#empty");
let filter = "all";

function apply() {
  const query = search.value.trim().toLowerCase();
  const visible = cards.filter((card) => {
    const statusOk = filter === "all" || card.dataset.status === filter;
    const text = card.dataset.search || "";
    return statusOk && (!query || text.includes(query));
  });
  const byRecent = (a, b) =>
    b.dataset.date.localeCompare(a.dataset.date) ||
    a.dataset.name.localeCompare(b.dataset.name, "ko");
  const byName = (a, b) => a.dataset.name.localeCompare(b.dataset.name, "ko");
  const byStatus = (a, b) =>
    a.dataset.rank.localeCompare(b.dataset.rank) || byRecent(a, b);
  const sorter = sort.value === "name" ? byName : sort.value === "status" ? byStatus : byRecent;
  visible.sort(sorter);
  cards.forEach((card) => {
    card.hidden = true;
  });
  visible.forEach((card) => {
    card.hidden = false;
    grid.appendChild(card);
  });
  count.textContent = `보이는 아이 ${visible.length}마리`;
  empty.hidden = visible.length !== 0;
}

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    filter = chip.dataset.filter;
    chips.forEach((item) => item.setAttribute("aria-pressed", String(item === chip)));
    apply();
  });
});
search.addEventListener("input", apply);
sort.addEventListener("change", apply);
apply();
