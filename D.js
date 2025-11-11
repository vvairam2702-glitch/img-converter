export default async function handler(req, res) {
  try {
    const response = await fetch("https://api.example.com/data");
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    console.error("API Error:", error);
    res.status(500).json({ error: "Server failed to fetch data." });
  }
}
