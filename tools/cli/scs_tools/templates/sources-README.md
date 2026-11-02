# Source documents

Put the documents this workspace's context is drafted from in this folder: an AI use policy, a
quality manual, SOPs, project notes. Any format the AI assistant can read is fine.

- They stay on this machine. Git ignores everything here except this README (SCS 0.7, D-59).
- Each one is recorded in `intake.yaml` (`source_documents`), and every rule drafted from it
  names it in `derived_from`.
- A document that applies to the Domain and its Projects lives once, in `domain/sources/`.
