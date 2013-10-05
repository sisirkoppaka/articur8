// neo4j.groovy
//This is a Gremlin REPL to experiment with queries.
import org.neo4j.kernel.EmbeddedReadOnlyGraphDatabase
// Get the graph.db link from http://localhost:7474/webadmin/#/info/org.neo4j/Kernel/
db = new EmbeddedReadOnlyGraphDatabase('/usr/local/Cellar/neo4j/community-1.9.3-unix/libexec/data/graph.db')
g = new Neo4jGraph(db)