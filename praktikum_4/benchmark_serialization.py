import json
import xml.etree.ElementTree as ET

def generate_mock_data(count):
    """Generate mock data for testing."""
    data = []
    for i in range(1, count + 1):
        record = {
            "id": str(1000 + i),
            "nama": f"Mahasiswa Integrasi Nomor {i}",
            "jurusan": f"Sistem Informasi Enterprise",
            "status": "Aktif" if i % 2 == 0 else "Cuti"
        }
        data.append(record)
    return data

def serialize_to_json(dataset):
    """Serialize data to JSON format."""
    payload = json.dumps({"data": dataset}, ensure_ascii=False)
    return payload.encode("utf-8")

def serialize_to_xml(dataset):
    """Serialize data to XML format."""
    root = ET.Element("response")
    students_node = ET.SubElement(root, "students")
    for s in dataset:
        item = ET.SubElement(students_node, "student")
        for key, value in s.items():
            child = ET.SubElement(item, key)
            child.text = str(value)
    return ET.tostring(root, encoding="utf-8")

if __name__ == "__main__":
    record_batches = [10, 50, 100, 500]

    print("=" * 65)
    print(f"{'Data Count':<12} | {'XML (Bytes)':<12} | {'JSON (Bytes)':<12} | {'Reduksi Efisiensi (%)':<15}")
    print("=" * 65)

    for count in record_batches:
        dataset = generate_mock_data(count)
        xml_bytes = len(serialize_to_xml(dataset))
        json_bytes = len(serialize_to_json(dataset))

        reduction = ((xml_bytes - json_bytes) / xml_bytes * 100)

        print(f"{count:<12} | {xml_bytes:<12} | {json_bytes:<12} | {reduction: .2f}%")
    print("=" * 65)