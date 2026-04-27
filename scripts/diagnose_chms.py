import sys
import re
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Mock models to avoid imports issues
from ace.engine.detector import TopologicalDetector

class DeepTopologicalInspector(TopologicalDetector):
    def __init__(self, min_density=3):
        super().__init__(min_density)
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        print(message)

    def diagnose(self, html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 0. Simulate candidate identification
        candidates = []
        for tag in soup.find_all(True):
            if tag.name in ['html', 'body', 'script', 'style', 'head']: continue
            dens = self._text_density(tag)
            has_uuid = self.uuid_pattern.search(tag.get_text())
            if dens >= self.min_density or has_uuid:
                candidates.append(tag)

        self.log(f"Total candidates found: {len(candidates)}")

        # 1. Clustering with verbose logs
        clusters = []
        for cand in candidates:
            added = False
            sig = self._compute_signature(cand)
            for cluster in clusters:
                ref_sig = self._compute_signature(cluster[0])
                if cluster[0].parent == cand.parent and self._are_signatures_compatible(ref_sig, sig):
                    cluster.append(cand)
                    added = True
                    break
            if not added:
                clusters.append([cand])

        # 2. Score each cluster
        scored_clusters = []
        for i, cluster in enumerate(clusters):
            score = self._score_cluster(cluster)
            sig = self._compute_signature(cluster[0])
            snippet = cluster[0].get_text(strip=True)[:50]
            parent_sig = self._compute_signature(cluster[0].parent) if cluster[0].parent else "None"
            
            scored_clusters.append({
                "id": i,
                "score": score,
                "size": len(cluster),
                "sig": sig,
                "parent_sig": parent_sig,
                "snippet": snippet,
                "avg_density": sum(self._text_density(t) for t in cluster) / len(cluster)
            })

        # Sort by score
        scored_clusters.sort(key=lambda x: x["score"], reverse=True)

        self.log("\n--- TOP CLUSTERS (Evidence) ---")
        for sc in scored_clusters[:10]:
            self.log(f"Cluster {sc['id']}: Score={sc['score']:.2f}, Size={sc['size']}, Density={sc['avg_density']:.1f}")
            self.log(f"  Signature: {sc['sig']}")
            self.log(f"  Snippet: {sc['snippet']}")

        # Search for specific content tags (CHMS specific)
        self.log("\n--- SPECIFIC CONTENT SEARCH (data-section-id) ---")
        content_nodes = soup.find_all(attrs={'data-section-id': True})
        self.log(f"Nodes with 'data-section-id': {len(content_nodes)}")
        
        for node in content_nodes[:5]:
            node_sig = self._compute_signature(node)
            # Find which cluster this node belongs to
            target_cluster = None
            for sc in scored_clusters:
                # We need to find the cluster by searching through clusters list
                orig_cluster = clusters[sc['id']]
                if node in orig_cluster:
                    target_cluster = sc
                    break
            
            if target_cluster:
                self.log(f"Node {node.name}[{node.get('data-section-id')}]: Contained in Cluster {target_cluster['id']} (Score={target_cluster['score']:.2f})")
            else:
                self.log(f"Node {node.name}[{node.get('data-section-id')}]: MISSING from any cluster (Signature: {node_sig})")

if __name__ == "__main__":
    inspector = DeepTopologicalInspector()
    inspector.diagnose("/home/sidix/dev_focus/labs/focus/CHMS_Causal-Hybrid-Mapping-System/CHMS_Causal-Hybrid-Mapping-System.html")
