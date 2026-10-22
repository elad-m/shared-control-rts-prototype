[CmdletBinding()]
param(
    [string]$ModDirectory = 'C:\EscalatedModBig',
    [string]$GameDirectory,
    [string]$EscalatedDirectory
)

# Sets up Zero Hour Escalated 7.1.2 for the shared-control build.
#  1. Copies the player's own Escalated files (downloaded by GenLauncher) to the mod folder, as .big.
#  2. Builds !!!ZZSharedControlFixes.big next to them from those files:
#     - build hotkeys: R for power plants (Israel, Ukraine), M for Israel's C-RAM;
#     - skirmish AI for Russia, North Korea, Baath and Ukraine: their scripts still name the original
#       generals' buildings and units, so those AI players never build. See ESCALATED.md.
# Escalated's own files are not changed. Every player must end up with identical files, which the
# checksums below confirm.

$ErrorActionPreference = 'Stop'

# Zero Hour Escalated 7.1.2, as downloaded by GenLauncher (.gib renamed to .big).
$escalatedFiles = [ordered]@{
    '!!!SoundEffects.big'           = '1408791AAF2107EE5B75205BA5E666F5C5ADDDD1BE1972E2C063B7748F10CAEA'
    '!!!ZHEAmerica.big'             = '08EE566DBEC39893B3328B5A3DFD2C26478D491A6031A067EA2C319B89CCE2F8'
    '!!!ZHEArabLeague.big'          = '6746D050CBFD22DA47A1F27AB56F2549CBCB7B37CCE1B28E54E725960E7EA1F8'
    '!!!ZHEArmor.big'               = '275B9956A772306DFCD0BB7B97D65F6DC4EF919D5A1137E96AB498DF2088AD68'
    '!!!ZHEAudio.big'               = '619BC43B6E41B7A22FAABFDD9137C4AA01926153419B4929B45E1021D6C54EFC'
    '!!!ZHEBaathIraq.big'           = 'CA6977C47BD7E6B338AEB84A25C25D5D066CFA33A66AEC0524E3EB38D194AD44'
    '!!!ZHEBlueDragons.big'         = 'F5DE7A33993514401F6C89B75349081F381878C2F63DD85BA0B06EC132D729CE'
    '!!!ZHEChallenge.big'           = '89A1D6001C9FAB1870A7558442C2FB21517AD9C62F32C37FA5ACA9CE37DC66A3'
    '!!!ZHEChina.big'               = '7BEE4F4CC6DDF2634F898595CDBA856BBD9D1A7A8B41AF311819E6C1685E0A54'
    '!!!ZHECommandButton.big'       = '72D2FE5E8AC5232DFFFACF6694552C200183ADB7CFCCEBEE1960B710B141A004'
    '!!!ZHECommandSet.big'          = '21A444A28C4E6AFE82E83231DE31739A9DF6DA7BA52B6D6EFBE3BC5B36C99BEC'
    '!!!ZHEControlBarScheme.big'    = 'CB4A1841CD8C05DD27224504A4DC566A58E7D0C0188DFF79E2767AAA70D95358'
    '!!!ZHEEva.big'                 = '1B14B4F2E1B81D1111B7AD465A3831867D395C72F16A84303ECFBE46D1F4C088'
    '!!!ZHEFXList.big'              = '2A4ACD71D568B485E89E5F441F599832B9D72AB56B85563FD2B844D67F47AF2A'
    '!!!ZHEGeneralsStr.big'         = '2BA82975B373BA9440E8DEB54C5A0AF3598356BB7509E238055AF80AF61EE631'
    '!!!ZHEGLA.big'                 = '96752494B581B179986F05D6167B9632DE8F078C99175C56E257E896460563CB'
    '!!!ZHEIraq.big'                = 'E10E852CA3963257EC30DDA1BCDBA4329ECB6866107654EF610DF6F2667F7988'
    '!!!ZHEIsrael.big'              = 'A82356DA00E3BA632A0CA0A79EBAD54B65221B16E62A600997237DD3DF6CCDC8'
    '!!!ZHELocomotor.big'           = '49CF2E96F0FD1813A42FFAE19E22B4BF80B89F6C28B8AC1EDC5B88A6E7FC0DCA'
    '!!!ZHEMappedImagesDefault.big' = '23EF4A1DF68DC5DFB050D7F1934E44C7E397F018E0AC53A4D0F822A5BAD533F5'
    '!!!ZHEMouse.big'               = 'D5F4E714B415BDF50CDDF94F34622A9D27B387807BCD98F62E7CE58692765C13'
    '!!!ZHEMultiplayer.big'         = 'E98DA5E12A104295347D94F35BB7A59763207457D23E45C23D61BC7451F6C75C'
    '!!!ZHENorthKorea.big'          = 'B478F947DB567CBC0FA53593516A6286EC62F92D83F9D87FF5E7CF475FEABBB2'
    '!!!ZHEObjectCreationList.big'  = 'BE461A854BD66A5FF61F4EC00F8EBDB21D08560D6FC19ACD45AC181A36B195EB'
    '!!!ZHEParticleSystem.big'      = '246447B92E194D8EC27D24D7D04DD1513D2F15F22FFA73F1673C77C71742B3BB'
    '!!!ZHEPlayerTemplate.big'      = 'C55289D597CC31FF5112FEFD9D31801D3911C846F49B280122CBC39318556BD0'
    '!!!ZHERussia.big'              = '5BDE723C758579E2CA88FD5B2B2B9BCD6D572DA27EDEA5D3569111C8CADCA114'
    '!!!ZHEScience.big'             = 'C338E476668B3C3508B4EB2DAB4B1C28A546A2DD58B27C0A2E1A8F18BAAB3F31'
    '!!!ZHEScripts.big'             = 'DE4DF97576E0263DF871A45D0487BFE6362BF0D048C8899FBF52C4DED5EC2F93'
    '!!!ZHESpecialPower.big'        = '0C847974984E70AFDEE22405D2024FAA4882DB002D383B46722BC038A7F0BBBE'
    '!!!ZHEStealthGeneral.big'      = '6BB63DDEBA05D8A83729CD337CDFE27C40F8CEA78D9B51A9B00F906D3CA058DA'
    '!!!ZHESystemExtra.big'         = 'D2EDE42E24C6C1D82D758439C594A4CFDDD6603848E624D24C611DF7415491A3'
    '!!!ZHETextures.big'            = '1D00745C59071061AE09828C83EADE03F0E126419052944F4CE9D58627A9C8BE'
    '!!!ZHEToxinTruck.big'          = '69DCFCA1CE266EBF0B1D8B94C1755BCC9A997BAF02374E22AC848F6E62409289'
    '!!!ZHEUkraine.big'             = '4C8C6AF04803BAF17ADAAE869A386E6386E17E4049813C69C598A6D01BB90A5C'
    '!!!ZHEUpgrade.big'             = '706456CE3C40495509FDA910243A767E8EBC131370BC302EFC882DA24F09A41B'
    '!!!ZHEVoice.big'               = '25FAABC848830A63416D0811612F30391AB33C490AD9AD84A4496F044DD7ECE7'
    '!!!ZHEW3D.big'                 = '8713C3811D185C815A208A4FD4A519F6F5C5662BA3F3F37AB76ACF19A129FCF7'
    '!!!ZHEWeapon.big'              = 'A691DAF42ABCB30BE6D898010F0F10ECB43C3AAE9F8D6AA797E4DCF3BF5137D0'
}
$fixesName = '!!!ZZSharedControlFixes.big'
$fixesHash = '9A628D968280D12D10D88E3FC0542CF1F40514337733068826D8D2349B782AFD'

Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

public static class EscalatedFixes
{
    static readonly Encoding Latin1 = Encoding.GetEncoding(28591);

    // ---------------------------------------------------------------- .big archives
    static uint BE(byte[] d, int p) { return (uint)(d[p] << 24 | d[p + 1] << 16 | d[p + 2] << 8 | d[p + 3]); }

    /// Reads the named files (case-insensitive, without a leading backslash) from a .big archive.
    public static Dictionary<string, byte[]> ReadBig(string path, string[] names)
    {
        byte[] d = File.ReadAllBytes(path);
        var wanted = new HashSet<string>(names, StringComparer.OrdinalIgnoreCase);
        var result = new Dictionary<string, byte[]>(StringComparer.OrdinalIgnoreCase);
        int count = (int)BE(d, 8), p = 16;
        for (int i = 0; i < count; i++)
        {
            int off = (int)BE(d, p), size = (int)BE(d, p + 4), end = Array.IndexOf(d, (byte)0, p + 8);
            string name = Latin1.GetString(d, p + 8, end - p - 8).TrimStart('\\');
            if (wanted.Contains(name)) { var b = new byte[size]; Buffer.BlockCopy(d, off, b, 0, size); result[name] = b; }
            p = end + 1;
        }
        return result;
    }

    /// Writes a .big archive holding the files in the given order.
    public static void WriteBig(string path, string[] names, byte[][] contents)
    {
        int header = 16;
        foreach (string n in names) header += 8 + Latin1.GetByteCount(n) + 1;
        int total = header + contents.Sum(c => c.Length);
        using (var w = new BinaryWriter(File.Create(path)))
        {
            w.Write(Encoding.ASCII.GetBytes("BIGF")); w.Write(total);
            WriteBE(w, names.Length); WriteBE(w, header);
            int off = header;
            for (int i = 0; i < names.Length; i++)
            {
                WriteBE(w, off); WriteBE(w, contents[i].Length);
                w.Write(Latin1.GetBytes(names[i])); w.Write((byte)0);
                off += contents[i].Length;
            }
            foreach (byte[] c in contents) w.Write(c);
        }
    }

    static void WriteBE(BinaryWriter w, int v) { w.Write(new[] { (byte)(v >> 24), (byte)(v >> 16), (byte)(v >> 8), (byte)v }); }

    /// Replaces old with new (ASCII), which must occur exactly once.
    public static byte[] ReplaceOnce(byte[] data, string oldText, string newText)
    {
        byte[] o = Latin1.GetBytes(oldText), n = Latin1.GetBytes(newText);
        int at = -1;
        for (int i = 0; i + o.Length <= data.Length; i++)
        {
            if (data[i] != o[0] || !Matches(data, i, o)) continue;
            if (at >= 0) throw new InvalidDataException("Found more than once: " + oldText);
            at = i;
        }
        if (at < 0) throw new InvalidDataException("Not found: " + oldText);
        var r = new byte[data.Length - o.Length + n.Length];
        Buffer.BlockCopy(data, 0, r, 0, at);
        Buffer.BlockCopy(n, 0, r, at, n.Length);
        Buffer.BlockCopy(data, at + o.Length, r, at + n.Length, data.Length - at - o.Length);
        return r;
    }

    static bool Matches(byte[] d, int at, byte[] what)
    {
        for (int j = 0; j < what.Length; j++) if (d[at + j] != what[j]) return false;
        return true;
    }

    // ---------------------------------------------------------------- SkirmishScripts.scb
    // A chunk file: a name table, then chunks of {uint id, ushort version, int size, body}.
    class Scb
    {
        public List<byte> D;
        public Dictionary<uint, string> Names = new Dictionary<uint, string>();
        public Dictionary<string, uint> Ids = new Dictionary<string, uint>();
        public int BodyStart;
        public List<string> Players = new List<string>();
        // One edit replaces [Start, End) and grows or shrinks every enclosing chunk.
        public List<Tuple<int, int, byte[], int[]>> Edits = new List<Tuple<int, int, byte[], int[]>>();

        public Scb(byte[] bytes)
        {
            D = new List<byte>(bytes);
            int n = I32(4), p = 8;
            for (int i = 0; i < n; i++)
            {
                int l = D[p]; string name = Latin1.GetString(bytes, p + 1, l); p += 1 + l;
                uint id = (uint)I32(p); p += 4;
                Names[id] = name; Ids[name] = id;
            }
            BodyStart = p;
            for (p = BodyStart; p < D.Count; p = End(p))
            {
                if (Kind(p) != "ScriptsPlayers") continue;
                int q = p + 10 + (Ver(p) >= 2 ? 4 : 0), cnt = I32(q); q += 4;
                for (int i = 0; i < cnt; i++) { Players.Add(Str(q)); q += 2 + U16(q); }
            }
        }

        public int I32(int p) { return D[p] | D[p + 1] << 8 | D[p + 2] << 16 | D[p + 3] << 24; }
        public int U16(int p) { return D[p] | D[p + 1] << 8; }
        public string Str(int p) { return Latin1.GetString(D.GetRange(p + 2, U16(p)).ToArray()); }
        public string Kind(int hp) { return Names[(uint)I32(hp)]; }
        public int Ver(int hp) { return U16(hp + 4); }
        public int Body(int hp) { return hp + 10; }
        public int End(int hp) { return hp + 10 + I32(hp + 6); }

        /// Offsets of the sub-chunks of a Script chunk (after its names, flags and delay).
        public List<int> ScriptChildren(int hp)
        {
            int p = Body(hp);
            for (int i = 0; i < 4; i++) p += 2 + U16(p);
            p += 6 + (Ver(hp) >= 2 ? 4 : 0);
            var r = new List<int>();
            for (; p < End(hp); p = End(p)) r.Add(p);
            return r;
        }

        /// Calls visit(scriptHeader, enclosingHeaders) for every script in every player's list.
        public void ForEachScript(Action<string, int, int[]> visit)
        {
            for (int p = BodyStart; p < D.Count; p = End(p))
            {
                if (Kind(p) != "PlayerScriptsList") continue;
                int i = 0;
                for (int list = Body(p); list < End(p); list = End(list), i++)
                {
                    string player = i < Players.Count ? Players[i] : "";
                    for (int c = Body(list); c < End(list); c = End(c))
                    {
                        if (Kind(c) == "Script") visit(player, c, new[] { p, list });
                        else if (Kind(c) == "ScriptGroup")
                        {
                            int q = Body(c) + 2 + U16(Body(c)) + 1 + (Ver(c) == 2 ? 1 : 0);
                            for (; q < End(c); q = End(q)) visit(player, q, new[] { p, list, c });
                        }
                    }
                }
            }
        }

        public void RenameString(int p, Dictionary<string, string> map, int[] stack)
        {
            string s;
            if (map == null || !map.TryGetValue(Str(p), out s)) return;
            Edits.Add(Tuple.Create(p, p + 2 + U16(p), LengthPrefixed(s), stack));
        }

        public void RenameParams(int p, Dictionary<string, string> map, int[] stack)
        {
            int cnt = I32(p); p += 4;
            for (int i = 0; i < cnt; i++)
            {
                int type = I32(p); p += 4;
                if (type == 16) { p += 12; continue; } // COORD3D
                p += 8;
                RenameString(p, map, stack);
                p += 2 + U16(p);
            }
        }

        public byte[] Apply()
        {
            foreach (var e in Edits.OrderByDescending(e => e.Item1))
            {
                int delta = e.Item3.Length - (e.Item2 - e.Item1);
                D.RemoveRange(e.Item1, e.Item2 - e.Item1);
                D.InsertRange(e.Item1, e.Item3);
                foreach (int hp in e.Item4)
                {
                    int size = I32(hp + 6) + delta;
                    for (int k = 0; k < 4; k++) D[hp + 6 + k] = (byte)(size >> (8 * k));
                }
            }
            return D.ToArray();
        }

        public byte[] Chunk(string kind, int version, byte[] body)
        {
            var r = new List<byte>();
            r.AddRange(BitConverter.GetBytes(Ids[kind]));
            r.AddRange(BitConverter.GetBytes((ushort)version));
            r.AddRange(BitConverter.GetBytes(body.Length));
            r.AddRange(body);
            return r.ToArray();
        }

        public byte[] Bytes(int from, int to) { return D.GetRange(from, to - from).ToArray(); }
    }

    static byte[] LengthPrefixed(string s)
    {
        byte[] b = Latin1.GetBytes(s);
        var r = new byte[b.Length + 2];
        r[0] = (byte)b.Length; r[1] = (byte)(b.Length >> 8);
        Buffer.BlockCopy(b, 0, r, 2, b.Length);
        return r;
    }

    /// Renames object names in the given players' scripts and in the teams they own.
    /// Shared target lists (OBJECTLIST_ADDOBJECTTYPE) name every faction's units on purpose and stay as they are.
    public static byte[] RenameObjects(byte[] scbBytes, Dictionary<string, Dictionary<string, string>> mapping)
    {
        var scb = new Scb(scbBytes);
        var maps = mapping.ToDictionary(k => k.Key,
            k => new Dictionary<string, string>(k.Value, StringComparer.OrdinalIgnoreCase));
        scb.ForEachScript((player, hp, enclosing) =>
        {
            Dictionary<string, string> map;
            if (!maps.TryGetValue(player, out map)) return;
            int[] stack = enclosing.Concat(new[] { hp }).ToArray();
            foreach (int c in scb.ScriptChildren(hp))
            {
                string kind = scb.Kind(c);
                if (kind == "OrCondition")
                {
                    for (int q = scb.Body(c); q < scb.End(c); q = scb.End(q))
                        scb.RenameParams(scb.Body(q) + 4 + (scb.Ver(q) >= 4 ? 4 : 0), map, stack.Concat(new[] { c, q }).ToArray());
                }
                else if (kind == "ScriptAction" || kind == "ScriptActionFalse")
                {
                    bool named = scb.Ver(c) >= 2;
                    string action = named ? scb.Names[(uint)scb.I32(scb.Body(c) + 4) >> 8] : null;
                    if (action != "OBJECTLIST_ADDOBJECTTYPE")
                        scb.RenameParams(scb.Body(c) + 4 + (named ? 4 : 0), map, stack.Concat(new[] { c }).ToArray());
                }
            }
        });
        for (int p = scb.BodyStart; p < scb.D.Count; p = scb.End(p))
        {
            if (scb.Kind(p) != "ScriptTeams") continue;
            for (int q = scb.Body(p); q < scb.End(p);)
            {
                int cnt = scb.U16(q); q += 2;
                var units = new List<int>(); string owner = null;
                for (int i = 0; i < cnt; i++)
                {
                    int kt = scb.I32(q); q += 4;
                    int type = kt & 0xFF; string key; scb.Names.TryGetValue((uint)kt >> 8, out key);
                    if (type == 0) q += 1;
                    else if (type == 1 || type == 2) q += 4;
                    else if (type == 3)
                    {
                        if (key == "teamOwner") owner = scb.Str(q);
                        if (key != null && key.StartsWith("teamUnitType")) units.Add(q);
                        q += 2 + scb.U16(q);
                    }
                    else if (type == 4) q += 2 + 2 * scb.U16(q);
                    else throw new InvalidDataException("Unknown team value type " + type);
                }
                Dictionary<string, string> map;
                if (owner != null && maps.TryGetValue(owner, out map))
                    foreach (int u in units) scb.RenameString(u, map, new[] { p });
            }
        }
        return scb.Apply();
    }

    /// The Easy and Normal openings of a GLA-based faction whose supply building needs a power plant:
    /// the barracks script also orders the power plant (copied from the Hard script, which already does),
    /// and the supply script waits for a power plant instead of starting at once.
    public static byte[] PowerPlantFirst(byte[] scbBytes, string player, string power, string supply)
    {
        var scb = new Scb(scbBytes);
        var scripts = new Dictionary<string, Tuple<int, int[]>>();
        scb.ForEachScript((p, hp, enclosing) =>
        {
            if (p == player) scripts[scb.Str(scb.Body(hp))] = Tuple.Create(hp, enclosing);
        });
        Func<string, Tuple<int, int[]>> script = name =>
        {
            if (!scripts.ContainsKey(name)) throw new InvalidDataException(player + ": no script '" + name + "'");
            return scripts[name];
        };

        byte[] powerName = LengthPrefixed(power);
        int hard = script("GLA Barracks - H").Item1;
        int powerAction = scb.ScriptChildren(hard).First(c => scb.Kind(c) == "ScriptAction"
            && IndexOf(scb.Bytes(c, scb.End(c)), powerName) >= 0);
        byte[] powerActionBytes = scb.Bytes(powerAction, scb.End(powerAction));

        // BUILT_BY_PLAYER <supply> from the War Factory script, retargeted at the power plant.
        int warFactory = script("GLA War Factory - N").Item1;
        int orTemplate = scb.ScriptChildren(warFactory).Single(c => scb.Kind(c) == "OrCondition");
        int cond = scb.Body(orTemplate);
        if (scb.End(cond) != scb.End(orTemplate)) throw new InvalidDataException("Unexpected War Factory condition");
        byte[] condBody = ReplaceLengthPrefixed(scb.Bytes(scb.Body(cond), scb.End(cond)), supply, power);
        byte[] waitForPower = scb.Chunk("OrCondition", scb.Ver(orTemplate), scb.Chunk("Condition", scb.Ver(cond), condBody));

        foreach (string x in new[] { "E", "N" })
        {
            var barracks = script("GLA Barracks - " + x);
            int firstAction = scb.ScriptChildren(barracks.Item1).First(c => scb.Kind(c) == "ScriptAction");
            scb.Edits.Add(Tuple.Create(firstAction, firstAction, powerActionBytes, barracks.Item2.Concat(new[] { barracks.Item1 }).ToArray()));

            var supplyScript = script("GLA Supply Center - " + x);
            int or = scb.ScriptChildren(supplyScript.Item1).Single(c => scb.Kind(c) == "OrCondition");
            scb.Edits.Add(Tuple.Create(or, scb.End(or), waitForPower, supplyScript.Item2.Concat(new[] { supplyScript.Item1 }).ToArray()));
        }
        return scb.Apply();
    }

    static byte[] ReplaceLengthPrefixed(byte[] data, string oldText, string newText)
    {
        byte[] o = LengthPrefixed(oldText), n = LengthPrefixed(newText);
        int at = IndexOf(data, o);
        if (at < 0 || IndexOf(data, o, at + 1) >= 0) throw new InvalidDataException("Expected one '" + oldText + "'");
        return data.Take(at).Concat(n).Concat(data.Skip(at + o.Length)).ToArray();
    }

    static int IndexOf(byte[] d, byte[] what, int from = 0)
    {
        for (int i = from; i + what.Length <= d.Length; i++) if (Matches(d, i, what)) return i;
        return -1;
    }
}
'@

function Write-Step([string]$Level, [string]$Message) {
    $color = @{ OK = 'Green'; FAIL = 'Red'; INFO = 'Gray' }[$Level]
    Write-Host ("[{0,-4}] {1}" -f $Level, $Message) -ForegroundColor $color
}

# --- Find the game and GenLauncher's Escalated download.
if ([string]::IsNullOrWhiteSpace($GameDirectory)) {
    foreach ($key in @(
            'HKLM:\SOFTWARE\Wow6432Node\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour',
            'HKLM:\SOFTWARE\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour',
            'HKCU:\SOFTWARE\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour')) {
        if (Test-Path -LiteralPath $key) {
            $candidate = (Get-ItemProperty -LiteralPath $key).InstallPath
            if (-not [string]::IsNullOrWhiteSpace($candidate)) { $GameDirectory = $candidate; break }
        }
    }
}
if ([string]::IsNullOrWhiteSpace($GameDirectory)) { throw 'Zero Hour was not found in the registry. Pass -GameDirectory "<path>".' }
$GameDirectory = [IO.Path]::GetFullPath($GameDirectory).TrimEnd('\')
$nested = Join-Path $GameDirectory 'Command and Conquer Generals Zero Hour'
if (-not (Test-Path -LiteralPath (Join-Path $GameDirectory 'INIZH.big')) -and (Test-Path -LiteralPath (Join-Path $nested 'INIZH.big'))) {
    $GameDirectory = $nested
}
Write-Step INFO "Zero Hour folder: $GameDirectory"
if ([string]::IsNullOrWhiteSpace($EscalatedDirectory)) {
    $EscalatedDirectory = Join-Path $GameDirectory 'GLM\Zero Hour Escalated\7.1.2'
}
if (-not (Test-Path -LiteralPath $EscalatedDirectory)) {
    throw "Escalated 7.1.2 was not found in $EscalatedDirectory. Download it with GenLauncher, or pass -EscalatedDirectory."
}

# --- The mod folder: outside the game folder, no spaces in its path.
if ($ModDirectory -match '\s') { throw "The mod folder path contains a space, which the game ignores: $ModDirectory" }
$ModDirectory = [IO.Path]::GetFullPath($ModDirectory).TrimEnd('\')
if ($ModDirectory.StartsWith($GameDirectory, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'The mod folder must be outside the game folder, for example C:\EscalatedModBig.'
}
New-Item -ItemType Directory -Force -Path $ModDirectory | Out-Null

# --- Copy Escalated's files, renamed from .gib to .big.
$failed = $false
foreach ($entry in $escalatedFiles.GetEnumerator()) {
    $target = Join-Path $ModDirectory $entry.Key
    $source = Join-Path $EscalatedDirectory ([IO.Path]::ChangeExtension($entry.Key, '.gib'))
    if (-not ((Test-Path -LiteralPath $target) -and (Get-FileHash -LiteralPath $target).Hash -eq $entry.Value)) {
        if (-not (Test-Path -LiteralPath $source)) { Write-Step FAIL "$($entry.Key): missing from $EscalatedDirectory"; $failed = $true; continue }
        Copy-Item -LiteralPath $source -Destination $target -Force
    }
    if ((Get-FileHash -LiteralPath $target).Hash -eq $entry.Value) { Write-Step OK $entry.Key }
    else { Write-Step FAIL "$($entry.Key) differs from Escalated 7.1.2 as tested."; $failed = $true }
}
foreach ($file in Get-ChildItem -LiteralPath $ModDirectory -Filter '*.big' -File) {
    if (-not $escalatedFiles.Contains($file.Name) -and $file.Name -ne $fixesName) {
        Write-Step FAIL "Unexpected archive in the mod folder: $($file.Name)"; $failed = $true
    }
}
if ($failed) { throw 'The Escalated files are not the tested version. Fix the lines marked FAIL.' }

# --- Build the fixes file from those files.
$strings = [EscalatedFixes]::ReadBig((Join-Path $ModDirectory '!!!ZHEGeneralsStr.big'), @('Data\generals.str'))['Data\generals.str']
$strings = [EscalatedFixes]::ReplaceOnce($strings, '" &Power generators"', '" Powe&r generators"')
$strings = [EscalatedFixes]::ReplaceOnce($strings, '" C-&RAM"', '" C-RA&M"')
$strings = [EscalatedFixes]::ReplaceOnce($strings, '"&Powerplant."', '"Powe&rplant."')

$aiData = [EscalatedFixes]::ReadBig((Join-Path $ModDirectory '!!!ZHEMappedImagesDefault.big'), @('Data\INI\Default\AIData.ini'))['Data\INI\Default\AIData.ini']
$aiData = [EscalatedFixes]::ReplaceOnce($aiData, 'BaseDefenseStructure1     = Nuke_ChinaGattlingCannon', 'BaseDefenseStructure1     = NorthKorea_TurretBunker')

$json = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'escalated-ai-fixes.json') -Raw | ConvertFrom-Json
$mapping = New-Object 'System.Collections.Generic.Dictionary[string,System.Collections.Generic.Dictionary[string,string]]'
foreach ($player in $json.PSObject.Properties) {
    $names = New-Object 'System.Collections.Generic.Dictionary[string,string]'
    foreach ($pair in $player.Value.PSObject.Properties) { $names[$pair.Name] = $pair.Value }
    $mapping[$player.Name] = $names
}
$scripts = [EscalatedFixes]::ReadBig((Join-Path $ModDirectory '!!!ZHEScripts.big'), @('Data\Scripts\SkirmishScripts.scb'))['Data\Scripts\SkirmishScripts.scb']
$scripts = [EscalatedFixes]::RenameObjects($scripts, $mapping)
$scripts = [EscalatedFixes]::PowerPlantFirst($scripts, 'SkirmishGLADemolitionGeneral', 'BaathIraqPowerPlant', 'BaathIraqsupplydepo')
$scripts = [EscalatedFixes]::PowerPlantFirst($scripts, 'SkirmishGLAToxinGeneral', 'UkrainePowerPlant', 'Chem_GLASupplyStash')

$fixesPath = Join-Path $ModDirectory $fixesName
[EscalatedFixes]::WriteBig($fixesPath,
    [string[]]@('Data\generals.str', 'Data\INI\Default\AIData.ini', 'Data\Scripts\SkirmishScripts.scb'),
    [byte[][]]@($strings, $aiData, $scripts))
if ((Get-FileHash -LiteralPath $fixesPath).Hash -ne $fixesHash) {
    throw "$fixesName came out different from the tested one. Report this; do not play with it."
}
Write-Step OK "$fixesName built (hotkeys and skirmish AI fixes)."
Write-Host ''
Write-Host "Escalated is ready in $ModDirectory." -ForegroundColor Green
