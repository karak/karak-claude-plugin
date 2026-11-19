# References

## Primary references (in priority order)

| Priority | Source | Use it for |
|---|---|---|
| 1 | Leslie Lamport, *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers* (2002) — https://lamport.azurewebsites.net/tla/book-21-07-04.pdf | The definitive reference for the TLA+ language and tools: `Init` / `Next`, invariants, TLC configuration |
| 2 | Chris Newcombe et al., "How Amazon Web Services Uses Formal Methods" (CACM, 2015) — https://cacm.acm.org/research/how-amazon-web-services-uses-formal-methods/ | Industrial evidence that small models find design bugs |
| 3 | Leslie Lamport, John Matthews, Mark Tuttle, Yuan Yu, "Specifying and Verifying Systems with TLA+" (2002) — https://lamport.azurewebsites.net/pubs/spec-and-verifying.pdf | The path from writing a spec to model checking it |
| 4 | Hillel Wayne, *Learn TLA+* — https://www.learntla.com/ | PlusCal, labels and atomicity, practical style |
| 5 | M. A. Kuppe, L. Lamport, D. Ricketts et al., "The TLA+ Toolbox" (2019) — https://lamport.org/pubs/toolbox.pdf | Running TLC from the IDE and exploring traces |

## Further reading

- TLA+ Wiki — Learning TLA+ and Model Checking: https://www.docs.tlapl.us/learning:start
- Awesome TLA+: https://github.com/tlaplus/awesome-tlaplus
- Leslie Lamport — TLA+ Papers: https://lamport.azurewebsites.net/tla/papers.html
- The tools: https://github.com/tlaplus/tlaplus/releases

## Inspiration

This skill was inspired by pstack's `create-formal-verification-skill`, and takes these ideas from it:

- stay true to the code;
- see each property fail once;
- keep findings as findings, without weakening them;
- be honest about scope;
- keep reruns cheap;
- record the point at which the model was last synced with the code.
