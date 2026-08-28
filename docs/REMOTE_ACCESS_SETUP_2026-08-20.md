# iPhone to MacBook remote access for Claude Code, 2026-08-20

Status: **Mac side complete and verified. iPhone side unresolved.**

Everything below was measured live on 2026-08-20, not recalled.

## The diagnosis that took the longest to reach

iPhone Termius failed with the connection log ending right after crypto
negotiation. Server-side, with `LogLevel VERBOSE` enabled, the real error was:

    sshd-session[70616]: fatal: PAM user mismatch

That means the username the client sends is not byte-identical to the Mac
account name. macOS Directory Services resolves a near-match (wrong case, or
trailing whitespace), PAM returns the canonical name, sshd sees the two
disagree and aborts. The log shows `Retrieve User by Name` succeeding first,
then the mismatch. That ordering is the signature.

Canonical account name, from `dscl . -read /Users/josie RecordName`:

    josie

The account carries a SECOND RecordName (an Apple ID GUID string), which is
why a non-canonical username half-resolves instead of failing cleanly.

**Fix, untested as of writing:** create a fresh host entry on the iPhone and
type `josie` into the Username field from scratch. Do not edit the existing
field, because trailing whitespace is invisible.

## macOS logs nothing about SSH auth by default

Both `log show --predicate 'process == "sshd"'` and a grep of the whole
unified log returned zero rows while authentication was actively failing.
To see anything you must first:

    echo 'LogLevel VERBOSE' | sudo tee /etc/ssh/sshd_config.d/300-verbose.conf
    sudo launchctl kickstart -k system/com.openssh.sshd
    log stream --predicate 'process CONTAINS "sshd"' --style compact

Remove the drop-in afterwards. As of this writing it is STILL IN PLACE.

## Verified working on the Mac

| Component | Evidence |
|---|---|
| sshd key auth | `ssh -i ~/.ssh/termius_iphone josie@127.0.0.1` returns `KEY_WORKS` |
| Full Disk Access over SSH | SSH session can read `~/Library/Application Support/com.apple.TCC/` |
| Tailscale | `100.106.253.10`, MagicDNS `josephines-macbook-air` |
| iPhone on tailnet | `iphone171-1`, `100.77.198.110`, online |
| mosh | installed 1.4.0_40 |
| sleep | `pmset -c sleep 0` applied |

## The Keychain finding, which is the important one for Claude Code

Claude Code stores its auth token in the **macOS login Keychain**. There is no
`~/.claude/.credentials.json` on this machine. Measured:

| Context | Keychain | `claude -p` |
|---|---|---|
| plain SSH shell | LOCKED, "User interaction is not allowed" | **`Not logged in · Please run /login`** |
| inside the tmux server | UNLOCKED, `no-timeout` | works |

The tmux server (PID 12752) was launched from a GUI session, so it inherits an
unlocked Keychain. sshd does not, because keychain unlock is bound to GUI login.

**Consequence:** from a remote shell, always create new Claude Code windows
INSIDE the existing tmux server:

    tmux new-window -t canford8 -n phone-work -c /Users/josie/can-it-ford

Running `claude` at the bare SSH prompt returns `Not logged in`. This is not a
Claude Code bug and no amount of re-login fixes it from the SSH side.

## PATH over SSH is not the interactive PATH

SSH sessions get only:

    /Users/josie/.local/bin  /usr/bin  /bin  /usr/sbin  /sbin

`/opt/homebrew/bin` is absent, so `tmux` and `mosh-server` were unreachable and
Mosh would have failed with "mosh-server not found". Fixed with symlinks into
`~/.local/bin`, which IS on the SSH PATH:

    ~/.local/bin/mosh-server -> /opt/homebrew/bin/mosh-server
    ~/.local/bin/tmux        -> /opt/homebrew/bin/tmux

## Helpers added

- `~/.local/bin/ford` attaches to `canford8` as an independent grouped client,
  recreating the base session if the tmux server died.
- `~/.local/bin/fordstat` read-only glance: branch, HEAD, dirty tracked files,
  and every window with its running command. Touches nothing.

## Termius vault is encrypted at rest

`~/Library/Application Support/Termius/IndexedDB/` stores host labels as
base64 ciphertext. The only plaintext is the account address. So the host and
key inventory CANNOT be enumerated from the Mac, and any advice about which
entry to edit has to come from what the user reads off the phone screen.

## Open items

1. iPhone host still fails. Fix is the fresh-host recipe above, untested.
2. `/etc/ssh/sshd_config.d/300-verbose.conf` still present, should be removed.
3. `PasswordAuthentication` is still `yes`. The tailnet contains three devices
   belonging to two other people (`ahamrah49@`, `lche29@`), and tailnet members
   can reach port 22 by default. Consider a `PasswordAuthentication no` drop-in
   once key auth from the phone is confirmed.
4. `authorized_keys` holds 3 keys, two of them both labelled `termius-iphone`
   (`ttK5ch...` and `HP+9CO...`). Prune once the working one is identified.
5. `canford8` window 0 (`board`) exited at some point during the session.
