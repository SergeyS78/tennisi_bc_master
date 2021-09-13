"""Вспомогательные функции"""

def object_to_array(data):
    """
        function objectToArray($obj) {
            if(is_object($obj)) $obj = (array) $obj;
            if(is_array($obj)) {
                $new = array();
                foreach($obj as $key => $val) {
                    $new[$key] = objectToArray($val);
                }
            }
            else $new = $obj;
            return $new;
        }
    """