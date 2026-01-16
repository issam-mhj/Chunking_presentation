from chonkie import (
    Visualizer,
    TokenChunker,          # Fixed-size token-based chunking
    SemanticChunker,       # Semantic similarity-based chunking
    RecursiveChunker,      # Recursive text splitting
    SentenceChunker,       # Sentence-level chunking
    CodeChunker            # Code structure-aware chunking
)

text = """
Retrieval-Augmented Generation (RAG) Lewis et al. (2020) has emerged as one of the leading approaches to improving reliability. Using a trusted text corpus to provide factual evidence, RAG guides the LLM's output, reducing hallucinations and ensuring closer alignment with the source material Tonmoy et al. (2024). In the context of long, structurally similar legal documents, identifying the relevant text passage as "needle in the haystack" becomes a top priority that we aim to address.

On a technical level, we quantify the retrieval quality with our Document-Level Retrieval Mismatch (DRM) metric and the character-level precision and recall. Then, we investigate a simple yet effective technique to improve retrieval quality, Summary-Augmented Chunking (SAC). We enrich text chunks in the trusted text corpus with document-level summaries. This preserves global context, lost in standard chunking, guiding the retriever toward the correct document without altering the underlying retrieval pipeline. This method is applied to question-answering tasks across a diverse set of legal documents, including privacy policies, non-disclosure agreements, and merger-and-acquisition contracts.

Key contributions: (i) First, we define and quantify Document-Level Retrieval Mismatch (DRM), a key failure mode we observe in standard RAG pipelines where the retrieved information originates from entirely wrong source documents. (ii) We propose Summary-Augmented Chunking (SAC) as a lightweight and modular solution that strongly reduces DRM by injecting global context directly into each chunk. (iii) We demonstrate SAC's effectiveness on LegalBench-RAG, a new benchmark comprising question-answering tasks across structurally similar legal documents.

We measure the performance on LegalBench-RAG via document-level DRM and character-level precision/recall between the retrieved and ground-truth text snippets (see Figure 1a), offering a holistic measure of retrieval quality. While our current work focuses exclusively on this retrieval analysis, we are currently working on adapting a benchmark such as the Australian Legal QA dataset for end-to-end performance evaluation in future work.

This approach injects crucial global context into each chunk, specifically to mitigate DRM by guiding the retriever to the correct source document. The method is highly practical, requiring only one additional LLM call per document and can be smoothly integrated into existing RAG pipelines with minimal computational overhead.

The generic prompt used for summarization is the following: "Summarize the main purpose and key obligations of this [document type] in exactly [char_length] characters." Because LLMs often deviate from the specified length, we allowed a tolerance of 20 characters. Outputs exceeding this limit were regenerated with a reduced char_length value.

4 Experimental Setup
We evaluate the performance of our methods covering a broad picture of retrieval quality: (i) Document-Level Retrieval Mismatch (DRM): As our primary metric, DRM directly measures the retriever's ability to identify the correct source document. A lower DRM indicates higher precision at the document level. (ii) Text-Level Precision: It measures the fraction of all the retrieved text that is part of the ground truth text span. High precision means that the retrieved context is concise and contains minimal irrelevant "noise". (iii) Text-Level Recall: It measures the fraction of ground truth text captured in the retrieved text. High recall indicates completeness.

We experimented with chunk sizes of 200, 500, and 800 characters, combined with prepended summaries of either 150 or 300 characters. The precision and recall results for all six configurations are reported in Table 1. For our final pipeline, we selected a chunk size of 500 characters, consistent with Pipitone and Alami (2024), and a 150-character summary, as this configuration yielded the most balanced trade-off between precision and recall.

5 Results
5.1 Automatic Evaluation
We demonstrate that SAC significantly reduces DRM compared to the baseline, showcasing its effectiveness in providing necessary global context. The results, reported in Figure 2b, show a dramatic reduction in DRM across a wide range of hyperparameters, effectively halving the mismatch rate. Crucially, this improvement in document-level accuracy translates directly to improved text-level retrieval quality.

Across all datasets, SAC improves precision by 12-28% and recall by 8-22%, depending on the document type. Privacy policies benefited most from SAC due to their repetitive structure, while M&A contracts saw smaller gains from their more unique clause arrangements. Figure 3 shows example retrievals where baseline chunking retrieves irrelevant boilerplate from wrong documents, while SAC consistently pulls from the correct source.

5.2 Ablation Studies
Removing the summary prefix reverts performance to baseline levels, confirming its causal role. Alternative global context injections (e.g., document titles only) yielded 4-7% DRM reductions, far below SAC's 50% average. Increasing summary length beyond 300 characters provided marginal gains (+2% precision) but doubled preprocessing cost.

6 Discussion
Standard fixed-size chunking destroys document-level context, making retrievers vulnerable to DRM in corpora with similar documents. SAC addresses this without retraining or complex reranking, making it ideal for production RAG systems. Limitations include summary generation cost (one LLM call per document) and potential summary hallucination, though we observed <1% error rate with GPT-4.

Future work includes end-to-end generation evaluation, multi-document retrieval, and adapting SAC for non-legal domains like scientific papers or financial reports. Integrating SAC with advanced retrievers (e.g., ColBERT) could yield multiplicative gains.

6 Conclusion
We addressed the critical challenge of retrieval reliability in RAG systems operating on large, structurally similar legal document databases. We identified and quantified Document-Level Retrieval Mismatch (DRM) as a dominant failure mode, where retrievers are often easily confused by legal boilerplate language and select text from entirely incorrect documents. Targeting this issue, we investigate Summary-Augmented Chunking (SAC), a simple and computationally efficient technique that prepends document-level summaries to each text chunk. By injecting global context, SAC drastically reduces DRM and consequently improves text-level retrieval precision and recall.

Appendix A Hyperparameter Chunk Size and Summary Size
[Table 1 data would go here showing configs: 200+150, 200+300, 500+150, etc. with precision/recall scores]

Appendix B Datasets
LegalBench-RAG comprises 420 QA pairs across 3 document types:
- Privacy Policies (140 docs, 15k avg chars): GDPR compliance notices
- NDAs (120 docs, 8k chars): Standard confidentiality agreements  
- M&A Contracts (160 docs, 22k chars): Merger agreements with boilerplate

All documents sourced from SEC EDGAR filings 2020-2024, anonymized. Queries generated via GPT-4 with document-specific prompts ensuring diverse span coverage (clauses 2-15).

This text mimics real legal docs with repetition, structure, and semantic density—test semantic chunking vs fixed-size to see how well it preserves "DRM" and "SAC" context across chunks.[web:57]
"""

# Create visualizer
viz = Visualizer()

print("=" * 80)
print("1. FIXED-SIZE CHUNKING (TokenChunker)")
print("=" * 80)
token_chunker = TokenChunker(chunk_size=100, chunk_overlap=20)
token_chunks = token_chunker.chunk(text)
viz.print(token_chunks)
viz.save("chunking_fixed_size.html", token_chunks)
print(f"\n✓ Created {len(token_chunks)} chunks\n\n")

print("=" * 80)
print("2. SEMANTIC CHUNKING")
print("=" * 80)
try:
    semantic_chunker = SemanticChunker(chunk_size=512, threshold=0.5)
    semantic_chunks = semantic_chunker.chunk(text)
    viz.print(semantic_chunks)
    viz.save("chunking_semantic.html", semantic_chunks)
    print(f"\n✓ Created {len(semantic_chunks)} chunks\n\n")
except Exception as e:
    print(f"⚠ Semantic chunking requires embeddings: {str(e)[:100]}...")
    print("   Install with: pip install sentence-transformers\n\n")
    semantic_chunks = []

print("=" * 80)
print("3. RECURSIVE CHUNKING")
print("=" * 80)
try:
    recursive_chunker = RecursiveChunker(chunk_size=512)
    recursive_chunks = recursive_chunker.chunk(text)
    viz.print(recursive_chunks)
    viz.save("chunking_recursive.html", recursive_chunks)
    print(f"\n✓ Created {len(recursive_chunks)} chunks\n\n")
except Exception as e:
    print(f"⚠ Recursive chunking failed: {str(e)[:100]}...\n\n")
    recursive_chunks = []

print("=" * 80)
print("4. SENTENCE-BASED CHUNKING")
print("=" * 80)
try:
    sentence_chunker = SentenceChunker(chunk_size=512, chunk_overlap=50)
    sentence_chunks = sentence_chunker.chunk(text)
    viz.print(sentence_chunks)
    viz.save("chunking_sentence.html", sentence_chunks)
    print(f"\n✓ Created {len(sentence_chunks)} chunks\n\n")
except Exception as e:
    print(f"⚠ Sentence chunking failed: {str(e)[:100]}...\n\n")
    sentence_chunks = []

print("=" * 80)
print("5. CODE STRUCTURE-AWARE CHUNKING")
print("=" * 80)
try:
    # Using 'python' language since CodeChunker works best with code
    # For plain text, it will chunk similarly to other methods
    code_chunker = CodeChunker(chunk_size=512, language='python')
    code_chunks = code_chunker.chunk(text)
    viz.print(code_chunks)
    viz.save("chunking_code.html", code_chunks)
    print(f"\n✓ Created {len(code_chunks)} chunks\n\n")
except Exception as e:
    print(f"⚠ Code chunking failed: {str(e)[:100]}...\n\n")
    code_chunks = []

print("=" * 80)
print("COMPARISON SUMMARY")
print("=" * 80)
print(f"Fixed-size (Token):  {len(token_chunks)} chunks")
print(f"Semantic:            {len(semantic_chunks) if semantic_chunks else '(skipped)'} chunks" if semantic_chunks else "Semantic:            (skipped - missing dependencies)")
print(f"Recursive:           {len(recursive_chunks) if recursive_chunks else '(skipped)'} chunks" if recursive_chunks else "Recursive:           (skipped)")
print(f"Sentence-based:      {len(sentence_chunks) if sentence_chunks else '(skipped)'} chunks" if sentence_chunks else "Sentence-based:      (skipped)")
print(f"Code-aware:          {len(code_chunks) if code_chunks else '(skipped)'} chunks" if code_chunks else "Code-aware:          (skipped)")
print("=" * 80)
