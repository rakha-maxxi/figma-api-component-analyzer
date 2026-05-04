# MAI Design Ops Handoff

Use this file as a context pack for another chat room or future thread.

## Role Context

I am working as `Design Ops` for `MAI Stream`.

My current responsibility is to:

- review MAI design files and UI kit condition
- identify inconsistencies and duplication
- analyze what should stay local vs move into `UI Kit`
- help PD and engineer work faster through better component readiness
- support gradual design system improvement, not a full redesign from scratch

## Key People

- `Mas Arief`: Head of Product Designer
- `Ce Veve`: PD Lead for Maxxi Agri / MAI
- `Mbak Maul`: Design Ops / DS reference from MTT stream
- `Mas Ojan` and `Mbak Billa`: my main Product Designer users in Maxxi Agri

## MAI Stream Context

MAI has multiple product platforms:

- `Backoffice`: website for admin operations
- `MMPlus`: tablet app for sales workflow
- `Distributor`: desktop-oriented website
- `Maxi Rewards`: mobile app for retailer
- `FS Plus`: mobile app for field agronomist
- `High Level Website`: responsive web for high-level approval
- `Maxi Monofactor`: sunset / no longer active

## Priority From Ce Veve

My first focus should be `MMPlus`.

Reason:

- many current and upcoming 2026 features depend on MMPlus
- MMPlus is the most strategic place to start for UI kit improvement

## Current MAI Design System Condition

- MAI design matured quickly under delivery pressure
- many files were created for speed, not system quality
- file structure is split by app and by feature/theme
- there is a `master` / `UI kit` structure already
- token system exists and is called `Magnum`
- tokens are more mature in MMPlus/mobile area
- UI kit exists but is not yet ideal
- designers still often use old components or local components
- adoption of the newer UI kit is still partial
- the system is not expected to become “perfect like MTT” immediately
- improvement should be incremental and realistic for designers and engineers

## Main Design Ops Insight

The MAI UI kit often contains components that are too large, too content-specific, or too close to full-page patterns.

This means:

- the UI kit is useful as a reference library
- but not yet optimal as a scalable design system

The recommended approach is:

- do not promote large compositions too quickly
- decompose large components into smaller reusable building blocks
- promote the reusable parts into `MM+ UI Kit`
- keep full page-level or feature-level compositions as `local pattern/reference` until they are more stable

## Current Design System Recommendation

For repeated large UI like headers, banners, dashboard blocks, or feature cards:

- avoid turning the entire assembled layout into one giant component too early
- first identify smaller reusable units such as:
  - `header shell`
  - `user identity block`
  - `text pairing`
  - `filter/scope selector`
  - `tab row`
  - `summary stat block`
  - `action group`
  - `dialog shell`
  - `card base`

Then:

- move reusable subparts into `UI Kit`
- keep the full composition as local component or pattern-level reference for now

## Decision Rules

### Promote to UI Kit if:

- used in 2+ files already
- same purpose
- same anatomy
- differences are mainly content or small layout variation
- likely to be reused again inside MMPlus / project

### Keep Local if:

- it is still page-specific
- structural differences are large
- it is still exploratory
- making a component would create a complicated “monster component”

### Promote Full Large Pattern Later if:

- the composition becomes stable across multiple files
- there is clear repeated use
- the variants are understandable and manageable

## Audit Approach

My audit method in MM+ is manual observation of design files.

When I find a repeated large pattern, I should ask:

1. Is this reused?
2. Is the reused part the whole block, or only some inner parts?
3. Are the differences content-level or structure-level?
4. Would componentizing this help designers, or create a monster component?

## Example Finding Logic

If a similar dashboard header/banner exists in 2 files with different content and layout:

- do not blindly merge into one big component
- identify shared anatomy
- discuss intent with designers first
- propose smaller reusable pieces to UI Kit
- keep the exact full layout local/pattern-level for now

## Communication Recommendation

Before changing component direction:

- talk with the product designer first
- understand the intent and future usage
- ask whether the pattern is expected to spread to more files
- ask which parts must stay flexible and which parts should be standardized

Recommended flow:

1. show the repeated pattern comparison
2. explain the shared anatomy
3. ask whether these are meant to solve the same problem
4. propose extraction of smaller reusable subcomponents
5. align with engineer if the new structure also affects implementation

## MM+ Audit Findings Already Identified

For `[MM+] Aktivitas Promosi FA Audit`, findings include:

- local-only components exist
- cross-file component usage exists
- components are pulled from other files like dashboard and registration flow
- some components are reused from master/UI kit
- some repeated plain elements should be extracted into reusable components
- examples include:
  - `text pairing`
  - `chips filter`
  - `table cell`
  - `bottom sheet`
  - `tab bar below app bar`
  - `bottom action bar / sticky CTA`
  - `empty/success/confirmation state`
  - `pop up dialog`
- inconsistency exists where an existing table cell component is not reused
- a deep-clicking issue exists in a log component because editing nested indicators is not efficient

## Current Working Principle

The goal is not:

- to make everything atomic immediately
- to rebuild all MAI files
- to chase perfect parity with MTT

The goal is:

- to improve MMPlus UI kit in a gradual, usable, realistic way
- to help designers design faster with clearer reusable building blocks
- to help engineers through more stable and communicable components

## Suggested Structure For MAI UI Kit

- `Foundations`
- `Primitives`
- `Compounds`
- `Patterns`
- `Templates / Reference`
- `Legacy / Transition`

This helps MAI separate:

- token-level system
- atomic building blocks
- reusable composed components
- larger approved patterns
- older temporary structures

## Useful References

These references support the decomposition approach:

- Brad Frost, `Atomic Design`
- Grundy & Hosking, `Developing adaptable user interfaces for component-based systems`
- van Welie & van der Veer, `Pattern Languages in Interaction Design`
- Dearden & Finlay, `Pattern Languages in HCI: A Critical Review`

## Prompt Template For Another Chat

You can paste this into another room:

> I’m working as Design Ops for MAI Stream. My current focus is auditing MMPlus UI kit and design files. MAI’s current UI kit contains a mix of atomic parts and very large feature-level components. My working recommendation is not to promote large components too quickly, but to decompose them into smaller reusable pieces first, such as header shell, text pairing, filter bar, summary block, dialog shell, or card base. Then I promote those reusable parts into the MM+ UI Kit, while keeping the full page-level composition as local pattern/reference until it becomes more stable. I need help reviewing findings, deciding local vs UI kit promotion, and writing actionable recommendations for PD Lead and Product Designers.

## Related Files

- audit PRD: [mmplus-audit-tool-prd.md](/Users/mtt/Documents/Codex/2026-04-24/i-m-faced-with-a-huge/mmplus-audit-tool-prd.md)
- if needed, audit data source: `/Users/mtt/Documents/MAI/mai-file-audit/mai-audit-data.json`
