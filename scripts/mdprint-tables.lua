-- mdprint: Tabellen im PDF setzen.
-- Spaltenbreiten wie im Browser (automatisches Tabellenlayout): jede Spalte bekommt
-- mindestens ihr längstes Wort, der Rest der Breite geht an die Spalten mit viel Text.
-- Dazu: linksbündig, Schrift \footnotesize, engerer Zeilenabstand in Zellen,
-- erstes Wort jeder Zelle trennbar, Kopfzeilen möglichst ungetrennt.
-- Metadatum mdprint-table-chars: Zeichen je Satzspiegelbreite (setzt mdprint; ca. 15 je Zoll).

local CHARS_PER_LINE = 70   -- Vorgabe für 6x9 in; wird aus den Metadaten überschrieben
local WORD_CAP = 11         -- längere Wörter im Tabellenkörper trennt LaTeX
local HEAD_CAP = 15         -- Kopfzeilen: Wörter bis zu dieser Länge bleiben ganz
local PAD = 1               -- Luft je Spalte in Zeichen

local function all_rows(tbl)
  local rows = {}
  for _, r in ipairs(tbl.head.rows) do table.insert(rows, { row = r, head = true }) end
  for _, b in ipairs(tbl.bodies) do
    for _, r in ipairs(b.head) do table.insert(rows, { row = r, head = true }) end
    for _, r in ipairs(b.body) do table.insert(rows, { row = r, head = false }) end
  end
  for _, r in ipairs(tbl.foot.rows) do table.insert(rows, { row = r, head = false }) end
  return rows
end

-- \hspace{0pt} vor dem ersten Wort: sonst trennt TeX das erste Wort eines Absatzes nie
local function make_breakable(cell)
  local b = cell.contents[1]
  if b and (b.t == "Plain" or b.t == "Para") then
    b.content:insert(1, pandoc.RawInline("latex", "\\hspace{0pt}"))
  end
end

local function set_table(tbl)
  local n = #tbl.colspecs
  if n == 0 then return nil end
  local minw, maxw = {}, {}
  for i = 1, n do minw[i] = 1; maxw[i] = 1 end
  for _, entry in ipairs(all_rows(tbl)) do
    local col = 1
    for _, cell in ipairs(entry.row.cells) do
      make_breakable(cell)
      local span = cell.col_span or 1
      if col <= n and span == 1 then
        local text = pandoc.utils.stringify(cell.contents)
        local len = utf8.len(text) or #text
        if len > maxw[col] then maxw[col] = len end
        local cap = entry.head and HEAD_CAP or WORD_CAP
        for word in text:gmatch("%S+") do
          for part in word:gmatch("[^%-/]+[%-/]?") do
            local l = math.min(utf8.len(part) or #part, cap)
            if l > minw[col] then minw[col] = l end
          end
        end
        -- kurze Kopfzeilen ("Vertieft in") bleiben einzeilig
        if entry.head and len <= HEAD_CAP and len > minw[col] then minw[col] = len end
      end
      col = col + span
    end
  end
  local summin, summax = 0, 0
  for i = 1, n do
    minw[i] = minw[i] + PAD; maxw[i] = math.max(maxw[i] + PAD, minw[i])
    summin = summin + minw[i]; summax = summax + maxw[i]
  end
  local widths = {}
  if summax <= CHARS_PER_LINE then
    -- alles passt in eine Zeile: natürliche Breite, auf Satzspiegel gestreckt
    for i = 1, n do widths[i] = maxw[i] / summax end
  elseif summin >= CHARS_PER_LINE then
    for i = 1, n do widths[i] = minw[i] / summin end
  else
    local rest, slack = CHARS_PER_LINE - summin, summax - summin
    for i = 1, n do widths[i] = (minw[i] + rest * (maxw[i] - minw[i]) / slack) / CHARS_PER_LINE end
  end
  for i = 1, n do
    tbl.colspecs[i] = { pandoc.AlignLeft, widths[i] }
  end
  return {
    pandoc.RawBlock("latex", "\\begingroup\\footnotesize\\linespread{1.15}\\selectfont\\setlength{\\tabcolsep}{4pt}\\renewcommand{\\arraystretch}{1.25}"),
    tbl,
    pandoc.RawBlock("latex", "\\endgroup"),
  }
end

-- Erst die Metadaten lesen, dann die Tabellen setzen
return {
  {
    Meta = function(meta)
      local c = meta["mdprint-table-chars"]
      if c then
        local v = tonumber(pandoc.utils.stringify(c))
        if v and v > 20 then CHARS_PER_LINE = v end
      end
    end,
  },
  { Table = set_table },
}
