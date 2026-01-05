use std::process::{Command, Stdio};

fn main() {
    // Spawn Rust scanner, Python brain, Node executor
    Command::new("python")
        .args(["-m", "python.engine.ultimate_arbitrage_engine"])
        .stdout(Stdio::inherit())
        .spawn()
        .expect("Failed to start Python brain");

    Command::new("node")
        .args(["node/tx/submitter.js"])
        .stdout(Stdio::inherit())
        .spawn()
        .expect("Failed to start Node executor");

    // Rust process remains alive as hot-path scanner
    loop { std::thread::park(); }
}
