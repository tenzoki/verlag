-- mdprint --epub: Tabellen für E-Reader.
-- Tabellen mit drei oder mehr Spalten werden zu "Karten": je Zeile ein Block mit der
-- ersten Zelle als fetter Überschrift und darunter "Spaltenkopf: Wert" für die übrigen
-- Zellen. Auf einem 6-Zoll-Reader sind breite Tabellen sonst nicht lesbar.
-- Zeilen, in denen nur die erste Zelle gefüllt ist, werden zu Zwischenüberschriften.
-- Zweispaltige Tabellen bleiben Tabellen.

local MIN_COLS = 3

local function inlines_of(cell)
  return pandoc.utils.blocks_to_inlines(cell.contents)
end

local function is_empty(cell)
  return pandoc.utils.stringify(cell.contents):match("^%s*$") ~= nil
end

function Table(tbl)
  local n = #tbl.colspecs
  if n < MIN_COLS then return nil end
  local heads = {}
  if #tbl.head.rows > 0 then
    for i, cell in ipairs(tbl.head.rows[1].cells) do heads[i] = inlines_of(cell) end
  end
  local out = {}
  if tbl.caption and tbl.caption.long and #tbl.caption.long > 0 then
    table.insert(out, pandoc.Div(tbl.caption.long, pandoc.Attr("", {"tabelle-titel"})))
  end
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      local cells = row.cells
      local rest_empty = true
      for i = 2, #cells do if not is_empty(cells[i]) then rest_empty = false end end
      if rest_empty then
        table.insert(out, pandoc.Div({pandoc.Para({pandoc.Strong(inlines_of(cells[1]))})}, pandoc.Attr("", {"karten-gruppe"})))
      else
        local blocks = {pandoc.Para({pandoc.Strong(inlines_of(cells[1]))})}
        for i = 2, #cells do
          if not is_empty(cells[i]) then
            local line = pandoc.Inlines({})
            if heads[i] and #heads[i] > 0 then
              line:insert(pandoc.Span(heads[i]:clone() .. pandoc.Inlines({pandoc.Str(":")}), pandoc.Attr("", {"karte-feld"})))
              line:insert(pandoc.Space())
            end
            line:extend(inlines_of(cells[i]))
            table.insert(blocks, pandoc.Para(line))
          end
        end
        table.insert(out, pandoc.Div(blocks, pandoc.Attr("", {"karte"})))
      end
    end
  end
  return pandoc.Div(out, pandoc.Attr("", {"tabelle-karten"}))
end
